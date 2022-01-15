#### Encode HDR HEVC for Apple devices
Color primaries are in units of 0.00002 while display luminance is in units of 0.0001.  I wish I knew why.  ST 2067-21 mentions this.
hvc1 is required for Apple devices

```
ffmpeg -hide_banner -i J001C031_140110_R6MS.mov -c:v libx265 -preset fast -crf 15 -tag:v hvc1 -pix_fmt yuv420p10le \
  -x265-params "colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc:max-cll=1000,400: \
  master-display=G(13250,34500)B(7500,3000)R(34000,16000)WP(15635,16450)L(10000000,50)" hvc1_hdr15.mp4
```

#### Dual audio 5.1 + stereo for Youtube
```
ffmpeg  -i video.mov -i audio_8ch.wav -c:v copy -c:a pcm_s24le -map 0:v -map 1:a -map 1:a \
  -map_channel 1.0.0:0.1 -map_channel 1.0.1:0.1 \
  -map_channel 1.0.2:0.2 -map_channel 1.0.3:0.2 -map_channel 1.0.4:0.2 -map_channel 1.0.5:0.2 \
  -map_channel 1.0.6:0.2 -map_channel 1.0.7:0.2 -b:a:0 192k -b:a:1 384k youtube_output.mov
```

#### Change HEVC tag
```
ffmpeg -i input.mov -c:v copy -c:a copy -tag:v hev1 output.mp4
```

#### Write PNG image sequence
```
ffmpeg -i video.mov -c:v png output/output%03d.png -nostats
```

#### Capture multiple streams from Decklink Quad, lossless encode with Nvidia GPU
- Install Decklink driver
- Name inputs in Desktop Video Setup
- Copy Decklink SDK headers to `/usr/local/include`
- Compile with `--prefix=/usr/local --enable-decklink --enable-nvenc --enable-nonfree`
- Name the inputs using Desktop Video Setup
```
ffmpeg -loglevel warning -stats -f decklink -i "DeckLink-Capture-($num)" -format_code Hp59 \
  -pix_fmt yuv444p16le -an -c:v hevc_nvenc -preset losslesshp -gpu 0 -y "decklink$num.mp4"
```

#### Verify frame count metadata
```
ffprobe -select_streams v:0 -show_entries stream=nb_frames FilmicPro.mov -v error
```

#### Merge multi-mono audio tracks into 5.1 + stereo
a and b are arbitrary labels here
```
ffmpeg -y -hide_banner -i 12tracks.mov \
-filter_complex "[0:1][0:2][0:3][0:4][0:5][0:6] amerge=inputs=6[a]" \
-filter_complex "[0:7][0:8] amerge=inputs=2[b]" \
-map 0:v -map "[a]" -map "[b]" -c:a pcm_s16le -c:v copy output.mov
```

#### Display volume meters from Dolby CP950A AES67 stream
From an SDP file like this called `dolby1.sdp`:
```
v=0
o=- 0 0 IN IP4 10.49.51.51
s=CP950A_a
c=IN IP4 239.69.83.67/32
t=0 0
a=clock-domain:PTPv2 0
m=audio 6518 RTP/AVP 96
a=rtpmap:96 L24/48000/8
a=ts-refclk:ptp=IEEE1588-2008:00-60-DB-FF-FE-01-02-C8:0
a=mediaclk:direct=0
a=framecount:48
a=sync-time:0
```

```
ffmpeg -protocol_whitelist file,rtp,udp -i dolby1.sdp -filter_complex "showvolume=t=0:dm=1:ds=log" -f sdl -
```

To combine 4 separate streams:

```
ffmpeg -re -hide_banner -loglevel info -protocol_whitelist file,rtp,udp -i dolby1.sdp \
  -protocol_whitelist file,rtp,udp -i dolby2.sdp \
  -protocol_whitelist file,rtp,udp -i dolby3.sdp \
  -protocol_whitelist file,rtp,udp -i dolby4.sdp \
  -filter_complex "[0][1][2][3] amerge=inputs=4, showvolume=t=0:dm=1:ds=log" -f sdl -
```

Or you can use gstreamer to receive streams and pipe to ffmpeg
``` 
gst-launch-1.0 -q interleave name=i ! audioconvert ! wavenc ! fdsink \
  udpsrc address=239.69.83.67 port=6518 ! application/x-rtp, clock-rate=48000, channels=8 ! rtpjitterbuffer ! rtpL24depay ! audioconvert ! deinterleave name=d1 \
    d1.src_0 ! queue ! audioconvert ! i.sink_0 \
    d1.src_1 ! queue ! audioconvert ! i.sink_1 \
    d1.src_2 ! queue ! audioconvert ! i.sink_2 \
    d1.src_3 ! queue ! audioconvert ! i.sink_3 \
    d1.src_4 ! queue ! audioconvert ! i.sink_4 \
    d1.src_5 ! queue ! audioconvert ! i.sink_5 \
    d1.src_6 ! queue ! audioconvert ! i.sink_6 \
    d1.src_7 ! queue ! audioconvert ! i.sink_7 \
  udpsrc address=239.69.83.67 port=6520 ! application/x-rtp, clock-rate=48000, channels=8 ! rtpjitterbuffer ! rtpL24depay ! audioconvert ! deinterleave name=d2 \
    d2.src_0 ! queue ! audioconvert ! i.sink_8 \
    d2.src_1 ! queue ! audioconvert ! i.sink_9 \
    d2.src_2 ! queue ! audioconvert ! i.sink_10 \
    d2.src_3 ! queue ! audioconvert ! i.sink_11 \
    d2.src_4 ! queue ! audioconvert ! i.sink_12 \
    d2.src_5 ! queue ! audioconvert ! i.sink_13 \
    d2.src_6 ! queue ! audioconvert ! i.sink_14 \
    d2.src_7 ! queue ! audioconvert ! i.sink_15 \
  udpsrc address=239.69.83.67 port=6522 ! application/x-rtp, clock-rate=48000, channels=8 ! rtpjitterbuffer ! rtpL24depay ! audioconvert ! deinterleave name=d3 \
    d3.src_0 ! queue ! audioconvert ! i.sink_16 \
    d3.src_1 ! queue ! audioconvert ! i.sink_17 \
    d3.src_2 ! queue ! audioconvert ! i.sink_18 \
    d3.src_3 ! queue ! audioconvert ! i.sink_19 \
    d3.src_4 ! queue ! audioconvert ! i.sink_20 \
    d3.src_5 ! queue ! audioconvert ! i.sink_21 \
    d3.src_6 ! queue ! audioconvert ! i.sink_22 \
    d3.src_7 ! queue ! audioconvert ! i.sink_23 \
  udpsrc address=239.69.83.67 port=6524 ! application/x-rtp, clock-rate=48000, channels=8 ! rtpjitterbuffer ! rtpL24depay ! audioconvert ! deinterleave name=d4 \
    d4.src_0 ! queue ! audioconvert ! i.sink_24 \
    d4.src_1 ! queue ! audioconvert ! i.sink_25 \
    d4.src_2 ! queue ! audioconvert ! i.sink_26 \
    d4.src_3 ! queue ! audioconvert ! i.sink_27 \
    d4.src_4 ! queue ! audioconvert ! i.sink_28 \
    d4.src_5 ! queue ! audioconvert ! i.sink_29 \
    d4.src_6 ! queue ! audioconvert ! i.sink_30 \
    d4.src_7 ! queue ! audioconvert ! i.sink_31 \
| ffmpeg -hide_banner -loglevel info -i - -filter_complex showvolume=t=0:dm=3 -f sdl -
```
