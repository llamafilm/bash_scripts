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
