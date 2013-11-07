#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import walk
from time import sleep
from bregman.suite import os, Chromagram, HighQuefrencyChromagram, HighQuefrencyLogFrequencySpectrum, HighQuefrencyMelSpectrum, LinearFrequencySpectrum,\
LinearFrequencySpectrumCentroid, LinearFrequencySpectrumSpread, LinearPower, LogFrequencySpectrum, LogFrequencySpectrumCentroid, LogFrequencySpectrumSpread,\
LowQuefrencyLogFrequencySpectrum, LowQuefrencyMelSpectrum, MelFrequencyCepstrum, MelFrequencySpectrumCentroid, MelFrequencySpectrumSpread, RMS, dBPower
from contextlib import closing
from wave import open as wopen
from numpy import arange, median, mean
from subprocess import call
from pymongo import Connection
from aubio import tempo, source

class Extraction:

    def __init__(self):

        self.features_list = {'Chromagram':Chromagram,'HighQuefrencyChromagram':HighQuefrencyChromagram,'HighQuefrencyLogFrequencySpectrum':HighQuefrencyLogFrequencySpectrum,\
        'HighQuefrencyMelSpectrum':HighQuefrencyMelSpectrum,'LinearFrequencySpectrum':LinearFrequencySpectrum,'LinearFrequencySpectrumCentroid':LinearFrequencySpectrumCentroid,\
        'LinearFrequencySpectrumSpread':LinearFrequencySpectrumSpread,'LinearPower':LinearPower,'LogFrequencySpectrum':LogFrequencySpectrum,\
        'LogFrequencySpectrumCentroid':LogFrequencySpectrumCentroid,'LogFrequencySpectrumSpread':LogFrequencySpectrumSpread,'LowQuefrencyLogFrequencySpectrum':LowQuefrencyLogFrequencySpectrum,\
        'LowQuefrencyMelSpectrum':LowQuefrencyMelSpectrum,'MelFrequencyCepstrum':MelFrequencyCepstrum,'MelFrequencySpectrumCentroid':MelFrequencySpectrumCentroid,\
        'MelFrequencySpectrumSpread':MelFrequencySpectrumSpread,'RMS':RMS,'dBPower':dBPower,'BPM':'BPM' } #replace BPM!!!!!!!

        self.parameters_list, self.features = [], []

        print "EXTRACTION"
        try:
            con = Connection()
        except:
            call(["osascript", "-e", 'tell app "Terminal" to do script "mongod"'])
            sleep(2)
            con = Connection()
        db = con.extraction_test #change the name of the database
        song1 = db.song1
        song2 = db.song2
        song3 = db.song3
        self.so = [song1, song2, song3]

        path_data = '/Users/jonathan/Documents/Toolbox/Document/data.txt' #replace with path to document
        da = open(path_data,'r')

        for lin in da:
            li = lin.split("--")
            li[len(li)-1] = li[len(li)-1].replace("\n",'')
            if li[0] == "Features":
                self.features = li[1:]
            elif li[0] == "Parameters":
                parameters = []
                for l in li[1:]:
                    if l == 'skip':
                        parameters.append({"default":""})
                    else:
                        param_dic = {}
                        par = l.split("-")
                        for p in par:
                            val = p.split(":")
                            param_dic.update({val[0]:int(val[1])})
                        parameters.append(param_dic)
                self.parameters_list.append(parameters)

        self.iteratori = 0

        for i in self.parameters_list:
            self.extract(i)
            self.iteratori += 1
        da.close()


    def bpm(self,path,param):
        try:
            win_s = param['wfft']
            samplerate = param['sampe_rate']
        except:
            win_s = 512                 # fft size
            samplerate = 11000
            
        hop_s = win_s / 2           # hop size


        s = source(path, samplerate, hop_s)
        samplerate = s.samplerate
        o = tempo("default", win_s, hop_s, samplerate)

        # tempo detection delay, in samples
        # default to 4 blocks delay to catch up with
        delay = 4. * hop_s

        # list of beats, in samples
        beats = []

        # total number of frames read
        total_frames = 0
        while True:
            samples, read = s()
            is_beat = o(samples)
            if is_beat:
                this_beat = int(total_frames - delay + is_beat[0] * hop_s)
                #print "%f" % (this_beat / float(samplerate))
                beats.append(this_beat)
            total_frames += read
            if read < hop_s: break

        #convert samples to seconds
        beats = map( lambda x: x / float(samplerate), beats)

        bpms = [60./(b - a) for a,b in zip(beats[:-1],beats[1:])]

        if samplerate == 11000:
            b = median(bpms)*4
        elif samplerate == 22000:
            b = median(bpms)*2
        else:
            b = median(bpms)
        return b



    def wind(self,feat,fil):
        f =feat.tolist()
        a,b = [],[]
        for j in arange(0,len(f)):
            try:
                a += f[j]
            except:
                a = f
        for h in arange(int(len(a)/fil)):
            try:
                if(h!=0):
                    k = sum(a[h*fil-fil/2:(h+1)*fil])/(fil+fil/2)
                else:
                    k = sum(a[h*fil:(h+1)*fil])/fil
            except:
                k = sum(a[h*fil-fil/2:len(a)])/len(a[h*fil-fil/2:len(a)])
            b.append(k)
        return b


    def extract_feat(self,x,para):
        fea_dic = {}
        i = 0
        for f in self.features:
            if f != 'BPM':
                if para[i] != {"default":""}:
                    fea_dic.update({f:self.features_list[f](x,**para[i])})
                else:
                    fea_dic.update({f:self.features_list[f](x)})
            else:
                fea_dic.update({f:self.bpm(x,para[i])})

            i += 1
        fea_dic1 = {}
        for fe in fea_dic:
            if 'Chromagram' in fe:
                fea_dic1.update({fe:self.wind(fea_dic[fe].CHROMA,50)})
            elif fe == 'MelFrequencyCepstrum (MFCC)':
                fea_dic1.update({fe:self.wind(fea_dic[fe].MFCC,100)})
            elif 'LinearFrequencySpectrum' in fe: 
                fea_dic1.update({fe:self.wind(fea_dic[fe].STFT,50)})
            elif fe == 'LinearPower' or fe == 'RMS' or fe == 'dBPower':
                fea_dic1.update({fe:self.wind(fea_dic[fe].POWER,10)})
            elif fe == 'BPM':
                fea_dic1.update({fe:fea_dic[fe]})
            else:
                fea_dic1.update({fe:self.wind(fea_dic[fe].CQFT,50)})
        return fea_dic1


    def extract(self,param): 

        i = 0

        direc = '/Users/jonathan/Documents/DesktopiMac/WAVE/files/' #replace with path to wave files

        for root,dirs,files in os.walk(direc): #replace the path
            for file1 in files:
                i += 1
                if file1[len(file1)-3:len(file1)] == "wav":
                    w = wopen(direc+file1,"r")
                    with closing(w) as f:
                        frame = f.getnframes()
                        rate = f.getframerate()
                    meta = file1.split("-*-")
                    features_dict = self.extract_feat(direc+file1,param)

                    dbfeat = {}
                    j = 0
                    a = None
                    for feat1 in self.features:
                        b = ''
                        a = param[j]
                        for p in a:
                            if p == "default" or "":
                                b = "default  "
                            else:
                                b += p +'-'+ str(a[p]) + ', '
                        dbfeat.update({feat1:{b[0:len(b)-2]:features_dict[feat1]}})
                        j += 1


                    try:
                        yea = meta[4][0:len(meta[4])-4]
                        gen = meta[3]
                    except:
                        yea = None
                        gen = meta[3][0:len(meta[3])-4]
                    try:
                        tit = meta[0]
                    except:
                        tit = None
                    try:
                        art = meta[1]
                    except:
                        art = None
                    try:
                        alb = meta[2]
                    except:
                        alb = None

                    self.so[self.iteratori].insert({
                        'id':i,
                        'metadata': {
                        'title':tit,
                        'artist':art,
                        'album':alb,
                        'genre':gen,
                        'year':yea,
                        'length':frame/float(rate)
                        },
                        'features': dbfeat,
                        })
                    print dbfeat
                    w.close()
        print "Extraction successfully completed!"

