# SubMagic
# 2020.10.30
# By Hirusha Fernando
# Python 3.8

import re
import os
from art import tprint


# Regex for timeline input validation
TIMELINE_INPUT_PATTERN = r'^(\d\d) (\d\d)\.(\d\d\d)$'
INPUT_REGEX = re.compile(TIMELINE_INPUT_PATTERN)


class SubMagic:
    
    def __init__(self, subPath):
        self.__subPath = subPath
        
        with open(subPath, 'r+', encoding='utf8') as sub:
            content = sub.read()
        
        self.__content = content    # For store subtitle file's content
        self.__timelinesSRT = []    # For store srt file's extracted timeline
        self.__timelinesSSA = []    # For store ssa file's extracted timeline
        self.__dialoguesSRT = []    # For store srt file's extracted dialogues
        self.__dialoguesSSA = []    # For store ssa file's extracted dialogues
        self.__splittedSRT = []     # For store srt file's splitted contents
        self.__splittedSSA = []     # For store ssa file's splitted contents

        self.__srtTimePattern = r'^(\d\d):(\d\d):(\d\d),(\d{3}) --> (\d\d):(\d\d):(\d\d),(\d{3})$'
        self.__timelineRegex = re.compile(self.__srtTimePattern)

        self.__srtDialoguePattern1 = r'">(.+)</f'
        self.__srtDialogueRegex1 = re.compile(self.__srtDialoguePattern1)

        self.__srtDialoguePattern2 = r'">(.+)'
        self.__srtDialogueRegex2 = re.compile(self.__srtDialoguePattern2)

        self.__srtDialoguePattern3 = r'(.+)</f'
        self.__srtDialogueRegex3 = re.compile(self.__srtDialoguePattern3)

        self.__ssaContentPattern = r'\bDialogue: Marked=0,\d:\d\d:\d\d\.\d\d,\d:\d\d:\d\d\.\d\d,Default,NTP,0000,0000,0000,!Effect,.+\b'
        self.__ssaContentRegex = re.compile(self.__ssaContentPattern)

        self.__ssaTimelinePattern = r'(\d):(\d\d):(\d\d)\.(\d\d),(\d):(\d\d):(\d\d)\.(\d\d)'
        self.__ssaTimelineRegex = re.compile(self.__ssaTimelinePattern)

        self.__ssaDialoguePattern1 = r"(?<=!Effect,)(.+)"
        self.__ssaDialogueRegex1 = re.compile(self.__ssaDialoguePattern1)

        self.__ssaDialoguePattern2 = r"(?<=!Effect,)<.>(.+)<"
        self.__ssaDialogueRegex2 = re.compile(self.__ssaDialoguePattern2)
        

    # Split srt file's content
    def __splitt_SRT(self):
        # split srt file
        self.__splittedSRT = self.__content.split('\n\n')
        
        # if last content is a Null value, remove it from list
        if not self.__splittedSRT[-1]:
            self.__splittedSRT.pop()

        print('[!] SRT SPLITTED')


    # Extract timelines from SRT file
    def __extract_timeline_SRT(self):
        # loop through each splitted srt file's content
        for splitted_srt_content in self.__splittedSRT:
            # split content into lines
            timeline = splitted_srt_content.split('\n')[1]            
            # insert# For store srt file dialogues timeline line into timeline list     
            self.__timelinesSRT.append(timeline)

        print('[!] TIMELINES EXTRACTED')

    
    # Extract dialogues from SRT file    
    def __extract_dialogues_SRT(self):
        # loop through each splitted srt file's content
        for splitted_srt_content in self.__splittedSRT:
            # split content into lines            
            dialogues = splitted_srt_content.split('\n')

            # for store dialogue, extracted using regex
            filtered_dialogues = []

            # Exttracting and inserting dialogues to filtered_dialogues
            for dialogue in dialogues:                
                if self.__srtDialogueRegex1.search(dialogue):
                    filtered = self.__srtDialogueRegex1.findall(dialogue)                    
                    filtered_dialogues.append(filtered[0])
                
                elif self.__srtDialogueRegex2.search(dialogue):
                    filtered = self.__srtDialogueRegex2.findall(dialogue)                    
                    filtered_dialogues.append(filtered[0])
                
                elif self.__srtDialogueRegex3.search(dialogue):
                    filtered = self.__srtDialogueRegex3.findall(dialogue)                    
                    filtered_dialogues.append(filtered[0])

                else:
                    filtered_dialogues.append(dialogue)

            print(filtered_dialogues[2:])
            dialogue = '\n'.join(filtered_dialogues[2:])            
            self.__dialoguesSRT.append(dialogue)
        
        print('[!] DIALOGUES EXTRACTED')


    def __write_to_srt(self, timeline:list, name:str, count:int):
        # number of dialogues in subtitle file
        dialogues_count = count
        
        # new subtitle file for output
        adjusted_sub = open(name, 'w+', encoding='utf8')
               
        # writing into new adjusted subtitle file
        for x in range(1,dialogues_count+1):            
            content_format = f'{x}\n{timeline[x-1]}\n{self.__dialoguesSRT[x-1]}\n\n'           
            adjusted_sub.write(content_format)
            #print(x)

        adjusted_sub.close()

        print('[!] FIXED SRT FILE CREATED')
        print('[!] DONE')

    
    def __write_to_ssa(self, name:str):
        new_ssa = open(name, 'w+', encoding='utf8')
        new_ssa.write('[Script Info]\n')
        new_ssa.write("; This is a Sub Station Alpha v4 script.\n")
        new_ssa.write(f"Title: {self.__subPath[:-4]}\n")
        new_ssa.write("ScriptType: v4.00\n")
        new_ssa.write("Collisions: Normal\n")
        new_ssa.write("PlayDepth: 0\n\n")
        new_ssa.write("[V4 Styles]\n")
        new_ssa.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, TertiaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, AlphaLevel, Encoding\n")
        new_ssa.write("Style: Default,Tahoma,18,16777215,65535,65535,-2147483640,-1,0,1,3,0,2,30,30,30,0,0\n\n")
        new_ssa.write("[Events]\n")
        new_ssa.write("Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        print("[!] SSA FILE INITIALIZED")

        for time, dialogue in zip(self.__timelinesSSA, self.__dialoguesSRT):
            part1 = "Dialogue: Marked=0,"
            part2 = ",Default,NTP,0000,0000,0000,!Effect,"
            dialogue = ' '.join(dialogue.split('\n'))
            subtitle = f'{part1}{time}{part2}{dialogue}\n'
            new_ssa.write(subtitle)

        new_ssa.close()
        print("[!] DONE")

    # split each timeline into hours, minutes, seconds
    def __split_srt_timeline_parts(self, timeline:str) -> tuple:
        
        splitted_time = self.__timelineRegex.findall(timeline)

        seconds1 = float('.'.join((splitted_time[0][2],splitted_time[0][3])))
        seconds2 = float('.'.join((splitted_time[0][-2],splitted_time[0][-1])))

        minutes1 = int(splitted_time[0][1])
        minutes2 = int(splitted_time[0][-3])

        hours1 = int(splitted_time[0][0])
        hours2 = int(splitted_time[0][-4])

        splitted = (seconds1, minutes1, hours1, seconds2, minutes2, hours2)

        return splitted


    # Split ssa file's content
    def __split_SSA(self):
        self.__splittedSSA = self.__content.split('\n')
        
        for x in self.__splittedSSA:
            if not x:
                self.__splittedSSA.remove(x)
        print(self.__splittedSSA[0])
                
        print('[!] SPLITTED SSA FILE')
        

    def __extract_timeline_SSA(self):
        for timeline in self.__splittedSSA:
            is_matched = self.__ssaTimelineRegex.search(timeline)
            if is_matched:
                temp = self.__ssaTimelineRegex.findall(timeline)                
                self.__timelinesSSA.append(temp[0])                
        print('[!] TIMELINE SPLITTED')        


    def __extract_dialogues_SSA(self):
        for dialogue in self.__splittedSSA:
            temp = ''
            if self.__ssaDialogueRegex2.search(dialogue):
                temp = self.__ssaDialogueRegex2.findall(dialogue)[0]
                temp = temp.replace(r'\N',' ')
                self.__dialoguesSSA.append(temp)                

            elif self.__ssaDialogueRegex1.search(dialogue):
                temp = self.__ssaDialogueRegex1.findall(dialogue)[0]
                temp = temp.replace(r'\N',' ')
                self.__dialoguesSSA.append(temp)            

        print('[!] DIALOGUES SPLITTED')


    def adjust_time(self, gap:str, fwd=True):
        sub_type = self.__subPath[-3:]        
        if sub_type == 'srt':
            self.__splitt_SRT()
            self.__extract_timeline_SRT()
            self.__extract_dialogues_SRT()
            new_srt_name = f'{self.__subPath[:-4]}-Adjusted.srt'

        else:
            self.__split_SSA()
            self.__extract_dialogues_SSA()
            self.__extract_timeline_SSA()        
            self.__ssa_timeline_to_srt()        
            self.__dialoguesSRT = self.__dialoguesSSA
            new_srt_name = f'{self.__subPath[:-4]}-Adjusted.ssa'

        # for store new timelines
        new_timelines = []        

        # split gap to minutes and seconds
        mins = int(gap.split()[0])
        sec = float(gap.split()[1])

        if not fwd:
            mins = -mins
            sec = -sec

        first_content = True

        # loop through the timeline
        for timeline in self.__timelinesSRT:
            splitted = self.__split_srt_timeline_parts(timeline)

            # timeline starting parts
            seconds1 = splitted[0]
            minutes1 = splitted[1]
            hours1 = splitted[2]

            # timeline ending parts
            seconds2 = splitted[3]
            minutes2 = splitted[4]
            hours2 = splitted[5]

            if first_content:
                first_sec1 = seconds1
                first_sec2 = seconds2
                first_min1 = minutes1
                first_min2 = minutes2
                first_hours1 = hours1
                first_hours2 = hours2

            # add seconds
            seconds1 += sec            
            # add minutes
            minutes1 += mins

            # checking starting seconds range
            if seconds1 > 59.999:
                seconds1 = 00.000
                minutes1 += 1
            elif seconds1 < 0:
                seconds1 += 60
                minutes1 -= 1

            # checking starting minutes range
            if minutes1 > 59:
                minutes1 = 00
                hours1 += 1
            elif minutes1 < 0:
                minutes1 += 60
                hours1 -= 1

            # checking if the timeline goes to minus values
            if hours1 < 0 and first_content:
                seconds1, minutes1, hours1 = 00.000, 00, 00
                mins = -first_min1
                sec = -first_sec1

            seconds2 += sec
            minutes2 += mins

            # checking ending seconds range
            if seconds2 > 59.999:
                seconds2 = 00.000
                minutes2 += 1
            elif seconds2 < 0:
                seconds2 += 60
                minutes2 -= 1

            # checking ending minutes range
            if minutes2 > 59:
                minutes2 = 00
                hours2 += 1
            elif minutes2 < 0:
                minutes2 += 60
                hours2 -= 1


            # rearrange seconds to suitable string format
            seconds1 = f'{seconds1:06.3f}'
            seconds2 = f'{seconds2:06.3f}'

            # concatanate the timeline
            new_timeline1 = f'{hours1:0>2}:{minutes1:0>2}:{seconds1[:2]},{seconds1[3:]}'
            new_timeline2 = f'{hours2:0>2}:{minutes2:0>2}:{seconds2[:2]},{seconds2[3:]}'
            adjusted_timeline = f'{new_timeline1} --> {new_timeline2}'

            # add adjusted timeline into new_timeline list
            new_timelines.append(adjusted_timeline)

            first_content = False        
        dialodues_count = len(self.__dialoguesSRT)
        self.__write_to_srt(new_timelines, new_srt_name, dialodues_count)
             
    # convert srt file to ssa file
    def srt2ssa(self):
        self.__splitt_SRT()
        self.__extract_timeline_SRT()
        self.__extract_dialogues_SRT()

        for timeline in self.__timelinesSRT:
            splitted = self.__split_srt_timeline_parts(timeline)

            # timeline starting parts
            seconds1 = splitted[0]
            ssa_seconds1 = f'{seconds1:05.2f}'
            minutes1 = splitted[1]
            ssa_minutes1 = f'{minutes1:0>2}'
            hours1 = splitted[2]
            ssa_start = f'{hours1}:{ssa_minutes1}:{ssa_seconds1}'

            # timeline ending parts
            seconds2 = splitted[3]
            ssa_seconds2 = f'{seconds2:05.2f}'
            minutes2 = splitted[4]
            ssa_minutes2 = f'{minutes2:0>2}'
            hours2 = splitted[5]
            ssa_end = f'{hours2}:{ssa_minutes2}:{ssa_seconds2}'

            ssa_timeline = f'{ssa_start},{ssa_end}'
            self.__timelinesSSA.append(ssa_timeline)
        
        print("[!] TIMELINE REARRANGED")
        
        ssa_name = f'{self.__subPath[:-4]}-Convereted.ssa'
        self.__write_to_ssa(ssa_name)

    
    def __ssa_timeline_to_srt(self):
        # Rearrange the timeline
        for timeline in self.__timelinesSSA:
            start = timeline[:4]            
            s_h, s_m = start[0], start[1]             
            s_s, s_ms = start[2], start[3]
            
            end = timeline[4:]
            e_h, e_m = end[0], end[1]
            e_s, e_ms = end[2], end[3]

            srt_start = f'{s_h:0>2}:{s_m}:{s_s},{s_ms:0<3}'
            srt_end = f'{e_h:0>2}:{e_m}:{e_s},{e_ms:0<3}'
            srt_timeline = f'{srt_start} --> {srt_end}'
            self.__timelinesSRT.append(srt_timeline)

        print("[!] TIMELINE REARRANGED")

        
    # Convert SSA file to SRT
    def ssa2srt(self):
        self.__split_SSA()
        self.__extract_dialogues_SSA()
        self.__extract_timeline_SSA()        
        self.__ssa_timeline_to_srt()        
        self.__dialoguesSRT = self.__dialoguesSSA

        srt_name = f'{self.__subPath[:-4]}-Convereted.srt'
        dialogues_count = len(self.__dialoguesSRT)
        self.__write_to_srt(self.__timelinesSRT, srt_name, dialogues_count)


    @staticmethod
    def initialize(subPath):
        if subPath[-3:] in ('srt','ssa'):
            try:
                with open(subPath, 'r+', encoding='utf8' errors='ignore') as sub:
                    content = sub.read()
                return SubMagic(subPath)

            except Exception as e:
                print(f'Error - {e}\n')
                return False
        else:
            return False


if __name__ == "__main__":
        
    tprint("SubMagic")
    print()

    while True:
        subPath = input("Input Subtitle File Path:")
        magic = SubMagic.initialize(subPath)   
        if magic == False: continue
        break
    
    print('[!] What do you want to do ?')
    print('\t[1] Adjust Subtitle Timeline')
    print('\t[2] SRT to SSA')
    print('\t[3] SSA to SRT')

    try:
        ui = input('\nYour Choice: ')
        while not ui in '123':
            print('[!] Invalid Input')
            os.system('PAUSE')
            ui = input('\nYour Choice: ')

        if ui == '1':
            while True:
                print('\n[!] Enter time to adjust. Input Format - MM SS.sss')
                print('[!] Example:- Think you want to adjust 1 minute and 2.456 seconds. Input it like this.')
                print('[!] 01 02.456')

                time = input('[+] Time to adjust: ')
                time_ok = INPUT_REGEX.match(time)
                if not time_ok:
                    print('[!] Invalid Format.')
                    os.system('PAUSE')
                    continue                
                break
            
            while True:
                direction = input('Forward(F) or Backward(B): ')
                
                if direction in 'fF':
                    magic.adjust_time(time)
                    break
                elif direction in 'bB':
                    magic.adjust_time(time, False)
                    break
                else:
                    print('[!] Invalid Input')
                    os.system('PAUSE')
                    print()
                    continue

        elif ui == '2':
            if subPath[-3:] != 'srt':
                print('[!] This file is not a srt file. Cannot convert to ssa.')
                os.system("PAUSE")
                exit()
            else:
                magic.srt2ssa()
        
        elif ui == '3':
            magic.ssa2srt()
    except Exception as e:
        print(e)
        
