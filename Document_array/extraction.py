#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import walk, path
from time import sleep
from bregman.suite import os, Chromagram, HighQuefrencyChromagram, HighQuefrencyLogFrequencySpectrum, HighQuefrencyMelSpectrum, LinearFrequencySpectrum,\
LinearFrequencySpectrumCentroid, LinearFrequencySpectrumSpread, LinearPower, LogFrequencySpectrum, LogFrequencySpectrumCentroid, LogFrequencySpectrumSpread,\
LowQuefrencyLogFrequencySpectrum, LowQuefrencyMelSpectrum, MelFrequencyCepstrum, MelFrequencySpectrumCentroid, MelFrequencySpectrumSpread, RMS, dBPower
from contextlib import closing
from wave import open as wopen
from numpy import arange, median, mean
from numpy import sum as npsum
from subprocess import call
from pymongo import Connection
from aubio import tempo, source
#from numpy.lib.stride_tricks import as_strided as ast

class Extraction:

    def __init__(self,y,path_w):
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

        path_data = path.dirname(path.realpath("data.txt")) + "/data.txt"
        path_wave = path_w #replace with path to wave files #######REPLACE#######
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

        if y == "new":
            self.extract_new(path_wave)
        elif y == "add":
            self.extract_add(path_wave)

        for i in song_test.find(): print i

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


    def sliding_window(self,x,coeff):
        new_array = []
        if x.shape != (x.shape[0],):
            xshape = x.shape
            for i in x:
                template = []
                for j in arange(int(len(i)/coeff)):
                    if(j!=0):
                        template.append(float(npsum(i[j*coeff-coeff/2:(j+1)*coeff])/(coeff+coeff/2)))
                    elif j == int(len(i)/coeff)-1:
                        template.append(float(npsum(i[j*coeff-coeff/2:])/len(i[j*coeff-coeff/2:])))
                    else:
                        template.append(float(npsum(i[:(j+1)*coeff])/coeff))
                new_array.append(template)
        else:
            xshape = (x.shape[0],1)
            template = []
            for j in arange(int(x.shape[0]/coeff)):
                if(j!=0):
                    template.append(float(npsum(x[j*coeff-coeff/2:(j+1)*coeff])/(coeff+coeff/2)))
                elif j == int(x.shape[0]/coeff)-1:
                    template.append(float(npsum(x[j*coeff-coeff/2:])/len(x[j*coeff-coeff/2:])))
                else:
                    template.append(float(npsum(x[:(j+1)*coeff])/coeff))
            new_array = template

        return new_array, xshape


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
                d,s = self.sliding_window(fea_dic[fe].CHROMA,16)
            elif fe == 'MelFrequencyCepstrum':
                d,s = self.sliding_window(fea_dic[fe].MFCC,16)
            elif 'LinearFrequencySpectrum' in fe:
                d,s = self.sliding_window(fea_dic[fe].STFT,16)
            elif fe == 'LinearPower' or fe == 'RMS' or fe == 'dBPower':
                d,s = self.sliding_window(fea_dic[fe].POWER,16)
            elif fe == 'BPM':
                d = fea_dic[fe]
                s = (0,0)
            else:
                d,s = self.sliding_window(fea_dic[fe].CQFT,16)
            fea_dic1.update({fe:{"data":d,"row":s[0],"column":s[1],"parameters":para[fe]}})
        return fea_dic1


    def parameter_short(self,a):
        b = ''
        for p in a:
            if p == "default" or "":
                b = "default"
            else:
                if p == "sample_rate":
                    b += "s" + str(a[p])[:len(str(a[p]))-3]
                elif p == "nbpo":
                    b += "nb" + str(a[p])
                elif p == "ncoef":
                    b += "nc" + str(a[p])
                elif p == "lcoef":
                    b += "lc" + str(a[p])
                elif p == "lo":
                    b += "lo" + str(a[p])
                elif p == "hi":
                    b += "hi" + str(a[p])[:len(str(a[p]))-3]
                elif p == "nfft":
                    b += "nf" + str(a[p])
                elif p == "wfft":
                    b += "w" + str(a[p])
                elif p == "nhop":
                    b += "nh" + str(a[p])
                elif p == "log10":
                    b += "l10" + str(a[p])[0]
                elif p == "magnitude":
                    b += "m" + str(a[p])[0]
                elif p == "intensity":
                    b += "i" + str(a[p])[0]
                elif p == "onsets":
                    b += "o" + str(a[p])[0]
                else:
                    b += "v" + str(a[p])
        return b

    def parameter_name(self,features_diction):
        mdbfeat = {}
        ii = 0
        for par in self.parameters_list:
            a = None
            # Convert parameters into a name, to classify the extracted features
            for feat1 in self.features:
                a = par[feat1]
                b = self.parameter_short(a)
                if ii > 0:
                    mdbfeat[feat1].append({b:features_diction[ii][feat1]})
                else:
                    mdbfeat.update({feat1:[{b:features_diction[ii][feat1]}]})
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

                    if len(meta) == 4:
                        tit = meta[0]
                        art = meta[1]
                        alb = meta[2]
                        gen = meta[3][:len(meta[3])-4]
                        yea = None
                    elif len(meta) == 5:
                        tit = meta[0]
                        art = meta[1]
                        alb = meta[2]
                        gen = meta[3]
                        yea = meta[4][:len(meta[4])-4]
                    elif len(meta) == 1:
                        tit = meta[0][:len(meta[0])-4]
                        art, alb, gen, yea = None, None, None, None
                    elif len(meta) == 2:
                        tit = meta[0]
                        art = meta[1][:len(meta[1])-4]
                        alb, gen, yea = None, None, None
                    elif len(meta) == 3:
                        tit = meta[0]
                        art = meta[1]
                        alb = meta[2][:len(meta[2])-4]
                        gen, yea = None, None

                    self.so.insert({
                        'song_id':i,
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
                    print i

        print "Extraction successfully completed!"




    def extract_add(self,direc):
        song_feature_dic = {}

        for root,dirs,files in os.walk(direc):
            for file1 in files:
                if file1[len(file1)-3:] == "wav":
                    features_dict = {}
                    ii = 0
                    for x in self.parameters_list:
                        features_dict.update({ii:self.extract_features(direc+file1,x)})
                        ii += 1
                    dbfeat = self.parameter_name(features_dict)
                    meta = file1.split("-*-")
                    song_feature_dic.update({meta[0]+meta[1]+meta[2]:dbfeat})
                    print "*"

        s = self.so.find()
        for song in s:
            x = song_feature_dic[(song["metadata"]["title"]+song["metadata"]["artist"]+song["metadata"]["album"]).encode('utf-8')]
            for i in x:
                a = "features."+i
                self.so.update({"metadata.title":song["metadata"]["title"],"metadata.artist":song["metadata"]["artist"],\
                    "metadata.album":song["metadata"]["album"]},{"$addToSet":{a:x[i]}})

        print "Extraction successfully completed!"




