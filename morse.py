import time
import machine

class Morse:
    def __init__(self, adcpin, minloudness):
        # Globals
        self.minloudness = minloudness
        # Local Attributes
        self.hearingactive = 0
        self.tones = []
        self.pauses = []    
        self.morsestring = ''
        self.decodedstring = ''
        # Init the ADC
        self.adc_pin = machine.Pin(adcpin)
        self.adc = machine.ADC(self.adc_pin)
        self.adc.atten(self.adc.ATTN_11DB)
        # Morse alphabet used:
        # https://de.wikipedia.org/wiki/Morsezeichen
        self.morsecode = []
        self.morsecode.append({'A': '.-'})
        self.morsecode.append({'B': '-...'})
        self.morsecode.append({'C': '-.-.'})
        self.morsecode.append({'D': '-..'})
        self.morsecode.append({'E': '.'})
        self.morsecode.append({'F': '..-.'})
        self.morsecode.append({'G': '--.'})
        self.morsecode.append({'H': '....'})
        self.morsecode.append({'I': '..'})
        self.morsecode.append({'J': '.---'})
        self.morsecode.append({'K': '-.-'})
        self.morsecode.append({'L': '.-..'})
        self.morsecode.append({'M': '--'})
        self.morsecode.append({'N': '-.'})
        self.morsecode.append({'O': '---'})
        self.morsecode.append({'P': '.--.'})
        self.morsecode.append({'Q': '--.-'})
        self.morsecode.append({'R': '.-.'})
        self.morsecode.append({'S': '...'})
        self.morsecode.append({'T': '-'})
        self.morsecode.append({'U': '..-'})
        self.morsecode.append({'V': '...-'})
        self.morsecode.append({'W': '.--'})
        self.morsecode.append({'X': '-..-'})
        self.morsecode.append({'Y': '-.--'})
        self.morsecode.append({'Z': '--..'})
        self.morsecode.append({'1': '.----'})
        self.morsecode.append({'2': '..---'})
        self.morsecode.append({'3': '...--'})
        self.morsecode.append({'4': '....-'})
        self.morsecode.append({'5': '.....'})
        self.morsecode.append({'6': '-....'})
        self.morsecode.append({'7': '--...'})
        self.morsecode.append({'8': '---..'})
        self.morsecode.append({'9': '----.'})
        self.morsecode.append({'0': '-----'})
        self.morsecode.append({'À': '.--.-'})
        self.morsecode.append({'Ä': '.-.-'})
        self.morsecode.append({'È': '.-..-'})
        self.morsecode.append({'É': '..-..'})
        self.morsecode.append({'Ö': '---.'})
        self.morsecode.append({'Ü': '..--'})
        self.morsecode.append({'ß': '...--..'})
        self.morsecode.append({'-CH-': '----'})
        self.morsecode.append({'Ñ': '--.--'})
        self.morsecode.append({'.': '.-.-.-'})
        self.morsecode.append({',': '--..--'})
        self.morsecode.append({':': '---...'})
        self.morsecode.append({';': '-.-.-.'})
        self.morsecode.append({'?': '..--..'})
        self.morsecode.append({'-': '-....-'})
        self.morsecode.append({'_': '..--.-'})
        self.morsecode.append({'(': '-.--.'})
        self.morsecode.append({')': '-.--.-'})
        self.morsecode.append({"'": '.----.'})
        self.morsecode.append({'=': '-...-'})
        self.morsecode.append({'+': '.-.-.'})
        self.morsecode.append({'/': '-..-.'})
        self.morsecode.append({'@': '.--.-.'})
        self.morsecode.append({'-KA-': '-.-.-'})
        self.morsecode.append({'-BT-': '-...-'})
        self.morsecode.append({'-AR-': '.-.-.'})
        self.morsecode.append({'-VE-': '...-.'})
        self.morsecode.append({'-SK-': '...-.-'})
        self.morsecode.append({'-SOS-': '...---...'})
        self.morsecode.append({'-HH-': '........'})
        
    # Sample at around 8 kHz (120 µS between samples)
    # Sample 50 times, which needs 0.006 seconds     
    def sample(self):
        values = []
        start = time.ticks_ms()
        for i in range(50):
            val = self.adc.read()
            values.append(val)
        return (time.ticks_ms() - start, max(values) - min(values))     

    def getloudness(self):
        # Sample for around 0.1 seconds and return loudness
        maxloudness = 0
        for i in range(16):
            timetaken, loudness = self.sample()  
            if loudness > maxloudness:
                maxloudness = loudness
        return maxloudness  

    def hearformorse(self):
        toneduration = 0
        pauseduration = 0
        intone = 0
        inpause = 0
        self.tones = []
        self.pauses = []
        # Check how loud it is
        minloud = self.getloudness()
        minloud = minloud + self.minloudness
        # Hear while our attribute is != 0 - an Interrupt can deactivate it
        self.hearingactive = 1
        while self.hearingactive != 0:
            timetaken, loudness = self.sample()
            
            if loudness > minloud:
                intone = 1
                if inpause == 1:
                    # We come from a pause, this is a new tone, save the old one
                    if toneduration > 0:
                        self.tones.append(toneduration)
                    toneduration = 0
                    inpause = 0
                toneduration = toneduration + timetaken
            else:
                inpause = 1
                if intone == 1:
                    # We come from a tone, this is a new pause, save the old one
                    if pauseduration > 0:
                        self.pauses.append(pauseduration)
                    pauseduration = 0
                    intone = 0
                pauseduration = pauseduration + timetaken
        # Done? Add the last pause and tone!
        self.tones.append(toneduration)
        self.pauses.append(pauseduration)
    
    def decodeintomorse(self):
        # Merge the two lists
        tones_and_pauses = []
        for pair in zip(self.pauses, self.tones):
            tones_and_pauses.extend(pair)   
        # Calculate the thresholds
        # For tones
        threshes = []
        for i in range(len(self.tones)-1):
            threshes.append({'jump': abs((self.tones[i+1] - self.tones[i]) / 2), 'val': abs((self.tones[i] + self.tones[i+1]) / 2)})
        threshes = sorted(threshes, reverse = True, key=lambda k: k['jump'])    
        tonethresh = threshes[0]['val']
        threshes.clear()
        # For pauses - remove the first and the last one, because it is a (very long) pause
        templist = self.pauses[1:-1]
        templist.sort() 
        threshes = []
        for i in range(len(templist)-1):
            threshes.append({'jump': abs((templist[i+1] - templist[i]) / 2), 'val': abs((templist[i] + templist[i+1]) / 2)})
        threshes = sorted(threshes, reverse = True, key=lambda k: k['jump']) 
        longpausethres = threshes[0]['val']
        mediumpausethres = threshes[1]['val']
        templist.clear()
        threshes.clear()        
        # Build morse string
        self.morsestring = ''
        i = -1
        for actsign in tones_and_pauses:
            i = i + 1
            if i % 2 != 0:
                # We're a tone
                if actsign > tonethresh:
                    self.morsestring = self.morsestring + '-'
                else:
                    self.morsestring = self.morsestring + '.'
            else:
                # We're a pause
                if actsign > longpausethres:
                    # New word
                    self.morsestring = self.morsestring + 'XZ'
                if actsign > mediumpausethres:
                    # New sign
                    self.morsestring = self.morsestring + 'X'       
        return self.morsestring
    
    def decodemorseintotext(self):
        self.decodedstring = ''
        for actval in self.morsestring.split('X'):
            if actval == 'Z':
                self.decodedstring = self.decodedstring + ' '
            else:
                for acttest in self.morsecode:
                    acttestval = list(acttest.values())[0]
                    acttestlen = len(acttestval)
                    acttestdecoded = list(acttest.keys())[0]    
                    if actval == acttestval:
                        self.decodedstring = self.decodedstring + acttestdecoded
        # Because of the first long pause we have a space at the beginning, remove it
        self.decodedstring = self.decodedstring[1:]
        return self.decodedstring               