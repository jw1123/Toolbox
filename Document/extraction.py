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
        # List of all the features that can be extracted so that they can be used as functions
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
                            # Store parameter name and value as a dictionary
                            param_dic.update({val[0]:int(val[1])})
                        # Store the dictionary in a list (one append = one feature)
                        parameters.append(param_dic)
                # In case there are several parameter-runs, append the parameters into a list (one append = one run, for the same features)
                self.parameters_list.append(parameters)

        # Iterator to keep tracking of the mongodb collection to use
        self.iteratori = 0

        for i in self.parameters_list:
            self.extract(i)
            self.iteratori += 1
        da.close()


    def BPM(self,path,param):
        """ Calculate the beats per minute (bpm) as a rhythm feature.
            path: path to the file
            param: dictionary of parameters
        """
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

        # Tempo detection delay, in samples
        # default to 4 blocks delay to catch up with
        delay = 4. * hop_s

        # List of beats, in samples
        beats = []

        # Total number of frames read
        total_frames = 0
        while True:
            samples, read = s()
            is_beat = o(samples)
            if is_beat:
                this_beat = int(total_frames - delay + is_beat[0] * hop_s)
                beats.append(this_beat)
            total_frames += read
            if read < hop_s: break

        # Convert samples to seconds
        beats = map( lambda x: x / float(samplerate), beats)

        bpms = [60./(b - a) for a,b in zip(beats[:-1],beats[1:])]

        if samplerate == 11000:
            b = median(bpms)*4
        elif samplerate == 22000:
            b = median(bpms)*2
        else:
            b = median(bpms)
        return b



    def window_sampling(self,feat,fil):
        """ Window sampling function.
            feat: list of feature values
            fil: filter/reduction value
        """
        f =feat.tolist()
        a,b = [],[]
        # Convert array to list
        for j in arange(0,len(f)):
            try:
                a += f[j]
            except:
                a = f
        # Sampling the feature with a window (50% overlap)
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


    def extract_features(self,x,para):
        """ Extract all features and reducing them invoking the wind function.
            x: path to the file
            para: list of parameter dictionaries
        """
        fea_dic = {}
        i = 0
        # Recognize the features and launch their respective functions
        for f in self.features:
            if f != 'BPM':
                if para[i] != {"default":""}:
                    # **para[i] gets the parameter dictionary and uses it as an argument for the bregman functions
                    fea_dic.update({f:self.features_list[f](x,**para[i])})
                else:
                    # Extraction with default values
                    fea_dic.update({f:self.features_list[f](x)})
            else:
                fea_dic.update({f:self.BPM(x,para[i])})

            i += 1
        fea_dic1 = {}
        # Reduce the size of the feature matrix and convert them to lists
        for fe in fea_dic:
            if 'Chromagram' in fe:
                fea_dic1.update({fe:self.window_sampling(fea_dic[fe].CHROMA,50)})
            elif fe == 'MelFrequencyCepstrum (MFCC)':
                fea_dic1.update({fe:self.window_sampling(fea_dic[fe].MFCC,100)})
            elif 'LinearFrequencySpectrum' in fe: 
                fea_dic1.update({fe:self.window_sampling(fea_dic[fe].STFT,50)})
            elif fe == 'LinearPower' or fe == 'RMS' or fe == 'dBPower':
                fea_dic1.update({fe:self.window_sampling(fea_dic[fe].POWER,10)})
            elif fe == 'BPM':
                fea_dic1.update({fe:fea_dic[fe]})
            else:
                fea_dic1.update({fe:self.window_sampling(fea_dic[fe].CQFT,50)})
        return fea_dic1


    def extract(self,param): 
        """ Iterating function, and inserting id, metadata and features to the collection.
            param: list of parameter dictionaries
        """
        i = 0

        direc = '/Users/jonathan/Documents/DesktopiMac/WAVE/files/' #replace with path to wave files

        for root,dirs,files in os.walk(direc):
            for file1 in files:
                i += 1
                if file1[len(file1)-3:len(file1)] == "wav":
                    w = wopen(direc+file1,"r")
                    # Exracting the file length
                    with closing(w) as f:
                        frame = f.getnframes()
                        rate = f.getframerate()
                    # Split the file name in order to use all the metadata
                    meta = file1.split("-*-")
                    # Launch the actual extraction
                    features_dict = self.extract_features(direc+file1,param)

                    dbfeat = {}
                    j = 0
                    a = None
                    # Convert parameters into a name, to classify the extracted features
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

