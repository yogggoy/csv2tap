open CSV file and print JTAG-TAP state

CSV collumn:         SimTime, JTAG_TRST_N, JTAG_TCK, JTAG_TMS, JTAG_TDI, JTAG_TDO, RSTI_N

    SimTime - time (not used)
    JTAG_TRST_N - TRST_N
    JTAG_TCK - TCK
    JTAG_TMS - TMS
    JTAG_TDI - TDI
    JTAG_TDO - TDO
    SERV_RSTI_N - reset_n (equal TRST_N)

example:
```
2450,1,1,1,x,z,0
2500,1,0,1,x,z,0
2550,1,1,1,x,z,0
```

    JTAG_TRST_N - PDown
    JTAG_TCK    - PDown
    JTAG_TMS    - PUp
    JTAG_TDI    - PUp
    JTAG_TDO    - none
    SERV_RSTI_N - PDown

PDown - z,x = 0

PUp - z,x = 1