#!/usr/bin/env python
# -*- coding: utf-8 -*-
import TSL2561
import PyBCM2835

def main():
        myTSL2561 = TSL2561.TSL2561()
        while(1):
                Lux=myTSL2561.readLux()
                PyBCM2835.delay(1000)
                print "Lux = " + str(Lux) 


if __name__ == '__main__':
    main()
