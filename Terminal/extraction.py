#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import walk
from time import sleep
from bregman.suite import os, Chromagram, HighQuefrencyChromagram, HighQuefrencyLogFrequencySpectrum, HighQuefrencyMelSpectrum, LinearFrequencySpectrum,\
LinearFrequencySpectrumCentroid, LinearFrequencySpectrumSpread, LinearPower, LogFrequencySpectrum, LogFrequencySpectrumCentroid, LogFrequencySpectrumSpread,\
LowQuefrencyLogFrequencySpectrum, LowQuefrencyMelSpectrum, MelFrequencyCepstrum, MelFrequencySpectrumCentroid, MelFrequencySpectrumSpread, RMS, dBPower
from contextlib import closing
from wave import open
from numpy import arange, mean, median
from subprocess import call
from pymongo import Connection
from aubio import tempo, source


class Extraction:

    def __init__(self):
        dic_feat = {'1':'Chromagram','2':'HighQuefrencyChromagram','3':'HighQuefrencyLogFrequencySpectrum',\
        '4':'HighQuefrencyMelSpectrum','5':'LinearFrequencySpectrum','6':'LinearFrequencySpectrumCentroid',\
        '7':'LinearFrequencySpectrumSpread','8':'LinearPower','9':'LogFrequencySpectrum',\
        '10':'LogFrequencySpectrumCentroid','11':'LogFrequencySpectrumSpread','12':'LowQuefrencyLogFrequencySpectrum',\
        '13':'LowQuefrencyMelSpectrum','14':'MelFrequencyCepstrum (MFCC)','15':'MelFrequencySpectrumCentroid',\
        '16':'MelFrequencySpectrumSpread','17':'RMS','18':'dBPower','19':'BPM'}
        self.features = {'Chromagram':Chromagram,'HighQuefrencyChromagram':HighQuefrencyChromagram,'HighQuefrencyLogFrequencySpectrum':HighQuefrencyLogFrequencySpectrum,\
        'HighQuefrencyMelSpectrum':HighQuefrencyMelSpectrum,'LinearFrequencySpectrum':LinearFrequencySpectrum,'LinearFrequencySpectrumCentroid':LinearFrequencySpectrumCentroid,\
        'LinearFrequencySpectrumSpread':LinearFrequencySpectrumSpread,'LinearPower':LinearPower,'LogFrequencySpectrum':LogFrequencySpectrum,\
        'LogFrequencySpectrumCentroid':LogFrequencySpectrumCentroid,'LogFrequencySpectrumSpread':LogFrequencySpectrumSpread,'LowQuefrencyLogFrequencySpectrum':LowQuefrencyLogFrequencySpectrum,\
        'LowQuefrencyMelSpectrum':LowQuefrencyMelSpectrum,'MelFrequencyCepstrum (MFCC)':MelFrequencyCepstrum,'MelFrequencySpectrumCentroid':MelFrequencySpectrumCentroid,\
        'MelFrequencySpectrumSpread':MelFrequencySpectrumSpread,'RMS':RMS,'dBPower':dBPower,'BPM':'BPM' } #replace BPM!!!!!!!

        print "EXTRACTION"
        print "You chose extraction. A terminal window will be opened to connect with MongoDB."
        
        try:
            con = Connection()
        except:
            call(["osascript", "-e", 'tell app "Terminal" to do script "mongod"'])
            sleep(1)
            con = Connection()
        db = con.extraction_test #change the name of the database
        song_features = db.song_features
        self.so = song_features

        print "The features that can be extracted are the following: "
        print "________________________________________________"
        print """
        1. Chromagram
        2. HighQuefrencyChromagram
        3. HighQuefrencyLogFrequencySpectrum
        4. HighQuefrencyMelSpectrum
        5. LinearFrequencySpectrum
        6. LinearFrequencySpectrumCentroid
        7. LinearFrequencySpectrumSpread
        8. LinearPower
        9. LogFrequencySpectrum
        10. LogFrequencySpectrumCentroid
        11. LogFrequencySpectrumSpread
        12. LowQuefrencyLogFrequencySpectrum
        13. LowQuefrencyMelSpectrum
        14. MelFrequencyCepstrum (MFCC)
        15. MelFrequencySpectrumCentroid
        16. MelFrequencySpectrumSpread
        17. RMS
        18. dBPower
        19. BPM
        """
        print "________________________________________________"
        print "You may now chose the features you wish to extract (referring to their number as listed above)"
        print "and type f when you're done: "

        y = None
        feat = []
        self.featlist = []
        while (y != 'f'):
            y = raw_input()
            if y != 'f':
                feat.append(y)
                self.featlist.append(dic_feat[y])

        print "You can now chose to set all the parameter values for each feature at your liking. The default values"
        print "(and the explanation) are as follows: "
        print "________________________________________________"
        print """
        'sample_rate': 44100, # The audio sample rate
        'nbpo': 12,           # Number of Bands Per Octave for front-end filterbank
        'ncoef' : 10,         # Number of cepstral coefficients to use for cepstral features
        'lcoef' : 1,          # Starting cepstral coefficient
        'lo': 62.5,           # Lowest band edge frequency of filterbank
        'hi': 16000,          # Highest band edge frequency of filterbank
        'nfft': 16384,        # FFT length for filterbank
        'wfft': 8192,         # FFT signal window length
        'nhop': 4410,         # FFT hop size
        'log10': False,       # Whether to use log output
        'magnitude': True,    # Whether to use magnitude (False=power)
        'intensify' : False,  # Whether to use critical band masking in chroma extraction
        'onsets' : False,     # Whether to use onset-synchronus features
        'verbosity' : 1       # How much to tell the user about extraction
        """
        print "________________________________________________"
        print "Type in first the name of the parameter (be careful to write it EXACTLY like it is written in the list above and in the same order)"
        print "and then the value you want to set (else the extraction will occur with default values) for each feature. "
        print "If you have no more paramaters you want to change for a specific feature, type in f two times: "

        param_list = []

        for fe in feat:
            a, b = None, None
            param_dict = {}
            print "_____________________________"
            print dic_feat[fe], ": "
            while (a != 'f'):
                a = raw_input("Parameter: ")
                if a !=f:
                    b = raw_input("Value: ")
                    try:
                        c = int(b)
                    except:
                        if b == "True":
                            c = True
                        else:
                            c = False
                    if a != 'f' and b != 'f':
                        param_dict.update({a:c})
            param_list.append(param_dict)

        self.extract(param_list)




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

    def extract_feat(self,x,para):
        fea_dic = {}
        i = 0
        for f in self.featlist:
            try:
                fea_dic.update({f:self.features[f](x,**para[i])})
            except:
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


    def extract(self,paramet): 

        i = 0

        print "Type in the directory to the folder with all your wave files: "
        direc = raw_input()
        print "The extraction can take a while, please wait..."

        for root,dirs,files in os.walk(direc): #replace the path
            for file1 in files:
                i += 1
                if file1[len(file1)-3:len(file1)] == "wav":
                    with closing(open(direc+file1,"r")) as f:
                        frame = f.getnframes()
                        rate = f.getframerate()
                    meta = file1.split("-*-")
                    features_dict = self.extract_feat(direc+file1,paramet)

                    dbfeat = {}
                    j = 0
                    a = None
                    for feat1 in self.featlist:
                        b = ''
                        a = paramet[j]
                        for p in a:
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

                    self.so.insert({
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
        print "Extraction successfully completed!"

