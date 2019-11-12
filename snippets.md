##### macOS I/O priority throttling
```bash
temporary: sudo sysctl -w debug.lowpri_throttle_enabled=0  
permanent: sudo sh -c 'echo "debug.lowpri_throttle_enable=0" >> /etc/sysctl.conf'  
```
##### SSH tunneling bind local port 9000 to port 80 of remote 192.168.1.1
`ssh -L [:]9000:192.168.1.1:80 user@hostname` (leading colon allows access from any IP)

##### Change macOS Terminal colors during SSH
.profile
```
function ssh_alias() {
    ssh $@;
    osascript -e "tell application \"Terminal\" to set current settings of window 1 to settings set \"man page\""
}
alias ssh=ssh_alias
```
/etc/ssh/ssh_config
`PermitLocalCommand yes`

.ssh/config
`osascript -e "tell application \"Terminal\" to set current settings of window 1 to settings set \"homebrew\""`

##### change Terminal prompt colors
This script shows a list of 256 color options, (8-bit colors maybe not supported everywhere)
```
color=16;
while [ $color -lt 245 ]; do
    echo -e "$color: \\033[38;5;${color}mhello\\033[48;5;${color}mworld\\033[0m"
    ((color++));
done
```
Set foreground red bold and background black: `export PS1="\[\e[1;38;5;160m\]\[\e[48;5;16m\][\u@\h \W]\[\e[0m\]$ "`
\u = username  
\h = host  
\W = current working directory  
The 1 before semicolon means bold  
160m is red, 16m is black  
Enclosing each command in escaped square brackets is necessary so the newline doesn't overflow


##### Use dtruss on Catalina
First disable SIP for dtruss (don't have to disable completely).  From recovery mode:
```
csrutil disable
csrutil enable --without dtrace
```
Now copy the binary somewhere and remove signature:
`codesign --remove-signature ~/ifconfig`
