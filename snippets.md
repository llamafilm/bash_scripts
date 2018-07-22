##### macOS I/O priority throttling
```bash
temporary: sudo sysctl -w debug.lowpri_throttle_enabled=0  
permanent: sudo sh -c 'echo "debug.lowpri_throttle_enable=0" >> /etc/sysctl.conf'  
```
##### SSH tunneling bind local port 9000 to port 80 of remote 192.168.1.1
`ssh -L [:]9000:192.168.1.1:80 user@hostname` (leading colon allows access from any IP)
