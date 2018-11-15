# -*- coding: utf-8 -*-
# python 3
import socket
import preprocess
import lstm
import music21
import collections
import itertools
import grammar
import generator
import qa
#import simpleOSC
import time

''' Helper function to parse a MIDI file into its measures and chords '''
def __parse_midi(data_fn):
    # Parse the MIDI data for separate melody and accompaniment parts.
    midi = music21.converter.parse(data_fn)

    notes = music21.stream.Voice()
    chords = music21.stream.Voice()
    for md in midi:
        for v in md.getElementsByClass(music21.stream.Voice):
            for m in v:
                if m.quarterLength == 0.0: m.quarterLength = 0.25
                if isinstance(m, music21.note.Note):
                    #print('note',m.offset,m.duration,m.pitch.midi)
                    notes.insert(m.offset, m)
                if isinstance(m, music21.chord.Chord):
                    #print('chord',m.offset,m.duration,m.pitchNames)
                    chords.insert(m.offset, m)
    
    #print('notes',len(notes),notes)
    #for m in notes: print(int(m.offset/4),m.offset,m.quarterLength,m)
    #print('chords',len(chords),chords)
    #for m in chords: print(int(m.offset/4),m.offset,m.quarterLength,m)
    
    # Group by measure so you can classify. 
    offsetTuples = [(int(m.offset / 4), m) for m in notes]
    notes_by_measure = collections.OrderedDict()
    i = 0
    for key_x, group in itertools.groupby(offsetTuples, lambda x: x[0]):
        #print(key_x,group,i)
        notes_by_measure[i] = [m[1] for m in group]
        i += 1
    #print('notes_by_measure',len(notes_by_measure),notes_by_measure)
    
    # Group chords by measure number.
    offsetTuples_chords = [(int(m.offset / 4), m) for m in chords]
    #print('offsetTuples_chords',len(offsetTuples_chords),offsetTuples_chords)
    chords_by_measure = collections.OrderedDict()
    i = 0
    for key_x, group in itertools.groupby(offsetTuples_chords, lambda x: x[0]):
        #print(key_x,group,i)
        chords_by_measure[i] = [m[1] for m in group]
        i += 1
    #print('chords_by_measure',len(chords_by_measure),chords_by_measure)

    # Fix for the below problem.
    #   1) Find out why len(measures) != len(chords).
    #   ANSWER: resolves at end but melody ends 1/16 before last measure so doesn't
    #           actually show up, while the accompaniment's beat 1 right after does.
    #           Actually on second thought: melody/comp start on Ab, and resolve to
    #           the same key (Ab) so could actually just cut out last measure to loop.
    #           Decided: just cut out the last measure. 
    if len(notes_by_measure) < len(chords_by_measure):
        del chords_by_measure[len(chords_by_measure) - 1]
    if len(notes_by_measure) > len(chords_by_measure):
        del notes_by_measure[len(notes_by_measure) - 1]
    assert len(notes_by_measure) == len(chords_by_measure)

    return notes_by_measure, chords_by_measure

def __parse_midi2(notes,chords):
    #print('notes2',len(notes),notes)
    #for m in notes: print(int(m.offset/4),m.offset,m.quarterLength,m)
    #print('chords2',len(chords),chords)
    #for m in chords: print(int(m.offset/4),m.offset,m.quarterLength,m)
    
    # Group by measure so you can classify. 
    offsetTuples = [(int(m.offset / 4), m) for m in notes]
    notes_by_measure = collections.OrderedDict()
    i = 0
    for key_x, group in itertools.groupby(offsetTuples, lambda x: x[0]):
        #print(key_x,group,i)
        notes_by_measure[i] = [m[1] for m in group]
        i += 1
    #print('notes_by_measure',len(notes_by_measure),notes_by_measure)
    
    # Group chords by measure number.
    offsetTuples_chords = [(int(m.offset / 4), m) for m in chords]
    #print('offsetTuples_chords',len(offsetTuples_chords),offsetTuples_chords)
    chords_by_measure = collections.OrderedDict()
    i = 0
    for key_x, group in itertools.groupby(offsetTuples_chords, lambda x: x[0]):
        #print(key_x,group,i)
        chords_by_measure[i] = [m[1] for m in group]
        i += 1
    #print('chords_by_measure',len(chords_by_measure),chords_by_measure)

    # Fix for the below problem.
    #   1) Find out why len(measures) != len(chords).
    #   ANSWER: resolves at end but melody ends 1/16 before last measure so doesn't
    #           actually show up, while the accompaniment's beat 1 right after does.
    #           Actually on second thought: melody/comp start on Ab, and resolve to
    #           the same key (Ab) so could actually just cut out last measure to loop.
    #           Decided: just cut out the last measure. 
    if len(notes_by_measure) < len(chords_by_measure):
        del chords_by_measure[len(chords_by_measure) - 1]
    if len(notes_by_measure) > len(chords_by_measure):
        del notes_by_measure[len(notes_by_measure) - 1]
    assert len(notes_by_measure) == len(chords_by_measure)

    return notes_by_measure, chords_by_measure

''' Helper function to get the grammatical data from given musical data. '''
def __get_abstract_grammars(measures, chords):
    # extract grammars
    abstract_grammars = []
    for ix in range(1, len(measures)):
        m = music21.stream.Voice()
        for i in measures[ix]:
            m.insert(i.offset, i)
        c = music21.stream.Voice()
        for j in chords[ix]:
            c.insert(j.offset, j)
        parsed = grammar.parse_melody(m, c)
        abstract_grammars.append(parsed)

    return abstract_grammars

''' Get musical data from a MIDI file '''
def get_musical_data(data_fn):
    measures, chords = __parse_midi(data_fn)
    abstract_grammars = __get_abstract_grammars(measures, chords)
    return chords, abstract_grammars

def get_musical_data2(notes, chords):
    measures, chords = __parse_midi2(notes,chords)
    abstract_grammars = __get_abstract_grammars(measures, chords)
    return chords, abstract_grammars
    
if __name__ == '__main__':
    #print('simpleOSC')
    #simpleOSC.initOSC()
    #simpleOSC.initOSCClient()
    #simpleOSC.setOSCHandler()
    #simpleOSC.processOSC()
    #simpleOSC.closeOSC()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    python_address = 'localhost', 7401
    max_address = 'localhost', 7402
    sock.bind(python_address)
    print('UDP ready')
    
    keysPushed = {}
    keys = {}
    bpm = 112
    quantizeUnit = 32
    startTime,endTime,unitTime = None,None,60/bpm/4
    print('bpm=',bpm,'unitTime=',unitTime,'quantizeUnit=',quantizeUnit)
    while True:
        data, address = sock.recvfrom(4096)
        if data:
            #print(len(data),type(data[0]))
            #for (i,d) in enumerate(data): print(i,d)
            #print(data.decode(encoding='ascii',errors='ignore'))
            if data[19] != 192:
                status = data[23]
                pitch = data[27]
                velocity = data[31]
                recTime = time.time()
                
                midiMessage = (status >> 4) & 0b1111
                midiChannel = status & 0b1111
                
                print('received midievent=',status,pitch,velocity)
                
                if pitch==0:
                    print("midi start")
                    startTime = recTime + 0.5
                elif pitch==127:
                    print("midi end")
                    endTime = recTime
                    break
                else:
                    if midiMessage==9:
                        keysPushed[(midiChannel,pitch)]=(velocity,recTime)
                    elif midiMessage==8 and (midiChannel,pitch) in keysPushed:
                        (prevVelocity,prevRecTime)=keysPushed.pop((midiChannel,pitch))
                        quantizedTime = round((prevRecTime-startTime)/(unitTime/quantizeUnit))
                        if quantizedTime not in keys: keys[quantizedTime] = []
                        keys[quantizedTime].append((pitch,(recTime-prevRecTime)))
        #if data:
            #sent = sock.sendto(data, client_address)
            #print('sent %s bytes back to %s' % (sent, client_address))

    notes2 = music21.stream.Voice()
    chords2 = music21.stream.Voice()
    prevTime = startTime
    for currTime in sorted(keys):
        if len(keys[currTime])==1:
            (pitch,duration) = keys[currTime][0]
            #print('note',pitch,duration/unitTime)
            n = music21.note.Note()
            n.pitch.midi = pitch
            n.quarterLength=round(duration/unitTime)/4
            n.offset = round(currTime/quantizeUnit)/4
            notes2.insert(n.offset, n)
        else:
            nList = []
            for (pitch,duration) in keys[currTime]:
                #print('chord',pitch,duration/unitTime)
                n = music21.note.Note()
                n.pitch.midi = pitch
                n.quarterLength=round(duration/unitTime)/4
                n.offset = round(currTime/quantizeUnit)/4
                nList.append(n)
            chords2.insert(round(currTime/quantizeUnit)/4, music21.chord.Chord(nList))
        prevTime = currTime

    print('midi process')
    # model settings
    N_epochs = 96
    max_len = 20
    max_tries = 300
    diversity = 0.5
        
    # get data
    #chords, abstract_grammars = get_musical_data('midi/metheny_short2.mid')
    chords, abstract_grammars = get_musical_data2(notes2,chords2)
    #print('chords',chords)
    #print('abstract_grammars',abstract_grammars)
    corpus, values, val_indices, indices_val = preprocess.get_corpus_data(abstract_grammars)
    #print('corpus length:', len(corpus), corpus)
    #print('total # of values:', len(values), values)

    # build model
    model = lstm.build_model(corpus=corpus, val_indices=val_indices, 
                             max_len=max_len, N_epochs=N_epochs)
    
    # set up audio stream
    out_stream = music21.stream.Stream()
    
    # generation loop
    curr_offset = 0.0
    loopEnd = len(chords)
    for loopIndex in range(1, loopEnd):
        # get chords from file
        curr_chords = music21.stream.Voice()
        for j in chords[loopIndex]:
            curr_chords.insert((j.offset % 4), j)
        
        while True:
            try:
                # generate grammar
                curr_grammar = generator.__generate_grammar(model=model, corpus=corpus, 
                                                  abstract_grammars=abstract_grammars, 
                                                  values=values, val_indices=val_indices, 
                                                  indices_val=indices_val, 
                                                  max_len=max_len, max_tries=max_tries,
                                                  diversity=diversity)
            
                curr_grammar = curr_grammar.replace(' A',' C').replace(' X',' C')
            
                # Pruning #1: smoothing measure
                curr_grammar = qa.prune_grammar(curr_grammar)
            
                # Get notes from grammar and chords
                curr_notes = grammar.unparse_grammar(curr_grammar, curr_chords)
            
                # Pruning #2: removing repeated and too close together notes
                curr_notes = qa.prune_notes(curr_notes)
            
                # quality assurance: clean up notes
                curr_notes = qa.clean_up_notes(curr_notes)
                
                break
            except:
                print('Exeception raised. try again!')
                continue
    
        # print # of notes in curr_notes
        print('After pruning: %s notes' % (len([i for i in curr_notes
            if isinstance(i, music21.note.Note)])))
    
        # insert into the output stream
        for m in curr_notes:
            out_stream.insert(curr_offset + m.offset, m)
        for mc in curr_chords:
            out_stream.insert(curr_offset + mc.offset, mc)
    
        curr_offset += 4.0
    
    out_stream.insert(0.0, music21.tempo.MetronomeMark(number=bpm))
    
    # Play the final stream through output (see 'play' lambda function above)
    #play = lambda x: music21.midi.realtime.StreamPlayer(x).play()
    #play(out_stream)
    
    # send OSC

    def addKey(keyDict, offset, length, pitch):
        key1 = int(offset*4)
        if key1 not in keyDict: keyDict[key1] = set()
        keyDict[key1].add((144,pitch,100))
        
        key2 = int((offset+length)*4)
        if key2 not in keyDict: keyDict[key2] = set()
        keyDict[key2].add((128,pitch,0))
            
    keyDict = {}
    for o in out_stream:
        if isinstance(o, music21.note.Note):
            #print(o.offset, o.quarterLength, o.pitch.midi)
            addKey(keyDict, o.offset, o.quarterLength, o.pitch.midi)
        elif isinstance(o, music21.chord.Chord):
            for o2 in o:
                #print(o2.offset, o2.quarterLength, o2.pitch.midi)
                addKey(keyDict, o2.offset, o2.quarterLength, o2.pitch.midi)
    
    data = [int(0) for i in range(32)]
    data[0] = 109
    data[1] = 105
    data[2] = 100
    data[3] = 105
    data[4] = 101
    data[5] = 118
    data[6] = 101
    data[7] = 110
    data[8] = 116
    data[12] = 44
    data[13] = 105
    data[14] = 105
    data[15] = 105
    m = max(keyDict)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for i in range(m+1):
        print(i)
        if i in keyDict:
            for key in keyDict[i]:
                (data[23],data[27],data[31]) = key
                print('sending midievent=',data[23],data[27],data[31])
                sock.sendto(bytes(data),max_address)
        time.sleep(unitTime)
    
    # save stream
    mf = music21.midi.translate.streamToMidiFile(out_stream)
    mf.open('midi/metheny_short2_out_'+str(N_epochs)+'.mid', 'wb')
    mf.write()
    mf.close()
