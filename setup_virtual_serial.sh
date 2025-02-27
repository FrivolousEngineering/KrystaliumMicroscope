#!/bin/bash

socat pty,raw,echo=0,link=number-input pty,raw,echo=0,link=number-output &
socat pty,raw,echo=0,link=rfid-1-input, pty,raw,echo=0,link=rfid-1-output &
socat pty,raw,echo=0,link=rfid-2-input, pty,raw,echo=0,link=rfid-2-output &
