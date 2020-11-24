#### Encode HDR HEVC for Apple devices
Color primaries are in units of 0.00002 while display luminance is in units of 0.0001.  I wish I knew why.  ST 2067-21 mentions this.

```
ffmpeg -hide_banner -i J001C031_140110_R6MS.mov -c:v libx265 -preset fast -crf 15 -tag:v hvc1 -pix_fmt yuv420p10le \
  -x265-params "colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc:max-cll=1000,400: \
  master-display=G(13250,34500)B(7500,3000)R(34000,16000)WP(15635,16450)L(10000000,50)" hvc1_hdr15.mp4
```
