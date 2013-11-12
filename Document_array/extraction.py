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
from cPickle import dumps
from bson.binary import Binary
#from numpy.lib.stride_tricks import as_strided as ast

class Extraction:

    def __init__(self,y):
        print "EXTRACTION"
        # List of all the features that can be extracted so that they can be used as functions
        self.features_list = {'Chromagram':Chromagram,'HighQuefrencyChromagram':HighQuefrencyChromagram,'HighQuefrencyLogFrequencySpectrum':HighQuefrencyLogFrequencySpectrum,\
        'HighQuefrencyMelSpectrum':HighQuefrencyMelSpectrum,'LinearFrequencySpectrum':LinearFrequencySpectrum,'LinearFrequencySpectrumCentroid':LinearFrequencySpectrumCentroid,\
        'LinearFrequencySpectrumSpread':LinearFrequencySpectrumSpread,'LinearPower':LinearPower,'LogFrequencySpectrum':LogFrequencySpectrum,\
        'LogFrequencySpectrumCentroid':LogFrequencySpectrumCentroid,'LogFrequencySpectrumSpread':LogFrequencySpectrumSpread,'LowQuefrencyLogFrequencySpectrum':LowQuefrencyLogFrequencySpectrum,\
        'LowQuefrencyMelSpectrum':LowQuefrencyMelSpectrum,'MelFrequencyCepstrum':MelFrequencyCepstrum,'MelFrequencySpectrumCentroid':MelFrequencySpectrumCentroid,\
        'MelFrequencySpectrumSpread':MelFrequencySpectrumSpread,'RMS':RMS,'dBPower':dBPower,'BPM':'BPM' } #replace BPM!!!!!!!

        self.parameters_list, self.features = [], []

        try:
            con = Connection()
        except:
            call(["osascript", "-e", 'tell app "Terminal" to do script "mongod"'])
            sleep(2)
            con = Connection()
        #__________________________________________________________
        db = con.extraction_test #change the name of the database #####REPLACE#####
        song_test = db.song_test #change the name of the collection ####REPLACE#####
        #__________________________________________________________
        self.so = song_test
        #_________________________________________________________________
        path_data = '/Users/jonathan/Documents/Toolbox/Document/data.txt' #replace with path to document ######REPLACE#######
        path_wave = '/Users/jonathan/Documents/DesktopiMac/WAVE/files/' #replace with path to wave files #######REPLACE#######
        #_________________________________________________________________
        da = open(path_data,'r')

        for lin in da:
            li = lin.split("--")
            li[len(li)-1] = li[len(li)-1].replace("\n",'')
            if li[0] == "Features":
                self.features = li[1:]
            elif li[0] == "Parameters":
                parameters = {}
                iii = 0
                for l in li[1:]:
                    if l == 'skip':
                        parameters.update({self.features[iii]:{"default":""}})
                    else:
                        param_dic = {}
                        par = l.split("-")
                        for p in par:
                            val = p.split(":")
                            # Store parameter name and value as a dictionary
                            param_dic.update({val[0]:int(val[1])})
                        # Store the dictionary in a dictionary (one update = one feature)
                        parameters.update({self.features[iii]:param_dic})
                    iii += 1
                # In case there are several parameter-runs, append the parameters into a list (one append = one run, for the same features)
                self.parameters_list.append(parameters)

        if y == "-enew":
            self.extract_new(path_wave)
        elif y == "-eadd":
            self.extract_add(path_wave)

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



    def extract_features(self,x,para):
        """ Extract all features and reducing them invoking the wind function.
            x: path to the file
            para: list of parameter dictionaries
        """
        fea_dic = {}

        # Recognize the features and launch their respective functions
        for f in self.features:
            if f != 'BPM':
                if para[f] != {"default":""}:
                    # **para[i] gets the parameter dictionary and uses it as an argument for the bregman functions
                    fea_dic.update({f:self.features_list[f](x,**para[f])})
                else:
                    # Extraction with default values
                    fea_dic.update({f:self.features_list[f](x)})
            else:
                fea_dic.update({f:self.BPM(x,para[f])})


        fea_dic1 = {}
        # Convert the numpy arrays into binaries to store them in MongoDB
        for fe in fea_dic:
            if 'Chromagram' in fe:
                fea_dic1.update({fe:Binary(dumps(fea_dic[fe].CHROMA, protocol=2))})
            elif fe == 'MelFrequencyCepstrum (MFCC)':
                fea_dic1.update({fe:Binary(dumps(fea_dic[fe].MFCC, protocol=2))})
            elif 'LinearFrequencySpectrum' in fe: 
                fea_dic1.update({fe:Binary(dumps(fea_dic[fe].STFT, protocol=2))})
            elif fe == 'LinearPower' or fe == 'RMS' or fe == 'dBPower':
                fea_dic1.update({fe:Binary(dumps(fea_dic[fe].POWER, protocol=2))})
            elif fe == 'BPM':
                fea_dic1.update({fe:fea_dic[fe]})
            else:
                fea_dic1.update({fe:Binary(dumps(fea_dic[fe].CQFT, protocol=2))})
        return fea_dic1

    def parameter_name(self,features_diction):
        mdbfeat = {}
        ii = 0
        for par in self.parameters_list:
            a = None
            # Convert parameters into a name, to classify the extracted features
            for feat1 in self.features:
                b = ''
                a = par[feat1]
                for p in a:
                    if p == "default" or "":
                        b = "default  "
                    else:
                        b += p +'-'+ str(a[p]) + ', '
                if ii > 0:
                    mdbfeat[feat1].update({b[0:len(b)-2]:features_diction[ii][feat1]})
                else:
                    mdbfeat.update({feat1:{b[0:len(b)-2]:features_diction[ii][feat1]}})
            ii += 1
        return mdbfeat


    def extract_new(self,direc): 
        """ Iterating function, and inserting id, metadata and features to the collection.
            param: list of parameter dictionaries
        """
        i = 0

        for root,dirs,files in os.walk(direc):
            for file1 in files:
                if file1[len(file1)-3:] == "wav":
                    i += 1
                    print i
                    w = wopen(direc+file1,"r")
                    # Exracting the file length
                    with closing(w) as f:
                        frame = f.getnframes()
                        rate = f.getframerate()

                    # Split the file name in order to use all the metadata
                    meta = file1.split("-*-")
                    # Launch the actual extraction
                    features_dict = {}
                    ii = 0

                    for x in self.parameters_list:
                        features_dict.update({ii:self.extract_features(direc+file1,x)})
                        ii += 1

                    dbfeat = self.parameter_name(features_dict)

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
                    w.close()

        print " Extraction successfully completed!"




    def extract_add(self,direc):
        song_feature_dic = {}

        for root,dirs,files in os.walk(direc):
            for file1 in files:
                if file1[len(file1)-3:] == "wav":
                    features_dict = {}
                    ii = 0
                    print "*",
                    for x in self.parameters_list:
                        features_dict.update({ii:self.extract_features(direc+file1,x)})
                        ii += 1
                    dbfeat = self.parameter_name(features_dict)
                    meta = file1.split("-*-")
                    song_feature_dic.update({meta[0]+meta[1]+meta[2]:dbfeat})

        s = self.so.find()
        for song in s:
            x = song_feature_dic[(song["metadata"]["title"]+song["metadata"]["artist"]+song["metadata"]["album"]).encode('utf-8')]
            for i in x:
                a = "features."+i
                self.so.update({"metadata.title":song["metadata"]["title"],"metadata.artist":song["metadata"]["artist"],\
                    "metadata.album":song["metadata"]["album"]},{"$addToSet":{a:x[i]}})


        print " Extraction successfully completed!"




