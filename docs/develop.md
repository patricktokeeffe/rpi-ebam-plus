# Development Roadmap

## E-BAM PLUS Raspberry Pi Interface

Notes to get you started:

* the USB serial port adapter is assigned to `/dev/ttyUSB0`
* the E-BAM PLUS expects:
    * baud settings 9600/8/N/1
    * hardware flow control none
* relevant E-BAM commands are in user manual Rev B pp 69-70
* you can get direct serial port access using `minicom`


A test script was created to probe for the EBAM's response to
serial port queries. Should make verifying hardware setup
easier (basically, answer the question: do we need a null
modem adapter?)
```
python src/test_ebam_comms.py
```

