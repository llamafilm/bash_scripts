#### Encode HDR HEVC for Apple devices
Color primaries are in units of 0.00002 while display luminance is in units of 0.0001.  I wish I knew why.  ST 2067-21 mentions this.

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
  -map_channel 1.0.6:0.2 -map_channel 1.0.7:0.2 youtube_output.mov
```
