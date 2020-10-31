# SubMagic
# 2020.10.30
# By Hirusha Fernando
# Python 3.8

import re
import os
from exceptions import SubtitlePathError


# Regex for timeline input validation
TIMELINE_INPUT_PATTERN = r'^(\d\d) (\d\d)\.(\d\d\d)$'
INPUT_REGEX = re.compile(TIMELINE_INPUT_PATTERN)


class SubMagic:
    
    def __init__(self, subPath):
        self.__subPath = subPath
        
        with open(subPath, 'r+', encoding='utf8') as sub:
            content = sub.read()
        
        self.__content = content    # For store srt file's content
        self.__timelinesSRT = []    # For store srt file's extracted timeline
        self.__timelinesSSA = []    # For store ssa file's extracted timeline
        self.__dialoguesSRT = []    # For store srt file's extracted dialogues
        self.__dialoguesSSA = []    # For store ssa file's extracted dialogues
        self.__splittedSRT = []     # For store srt file's splitted contents

        self.__srtTimePattern = r'^(\d\d):(\d\d):(\d\d),(\d{3}) --> (\d\d):(\d\d):(\d\d),(\d{3})$'
        self.__timelineRegex = re.compile(self.__srtTimePattern)

        

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

            # insert dialogue into dialogues list
            dialogue = '\n'.join(dialogues[2:])
            self.__dialoguesSRT.append(dialogue)
        
        print('[!] DIALOGUES EXTRACTED')


    def __write_to_srt(self, timeline):
        # number of dialogues in subtitle file
        dialogues_count = len(self.__splittedSRT)

        new_srt_name = f'{self.__subPath[:-4]}-Adjusted.srt'

        # new subtitle file for output
        adjusted_sub = open(new_srt_name, 'w+', encoding='utf8')
               
        # writing into new adjusted subtitle file
        for x in range(1,dialogues_count+1):
            # print(x)
            content_format = f'{x}\n{timeline[x-1]}\n{self.__dialoguesSRT[x-1]}\n\n'
            # print(timeline[x-1])
            # print(self.__dialoguesSRT[x-1])
            adjusted_sub.write(content_format)

        adjusted_sub.close()

        print('[!] FIXED SRT FILE CREATED')
        print('[!] DONE')

    
    def __write_to_ssa(self):
        new_ssa = open(f'{self.__subPath[:-4]}.ssa', 'w+', encoding='utf8')
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

        part1 = "Dialogue: Marked=0,"
        time1 = ""
        time2 = ""
        part2 = ",Default,NTP,0000,0000,0000,!Effect,"
        dialogue = ""

    
    def adjust_time(self, gap:str, fwd=True):        
        self.__splitt_SRT()
        self.__extract_timeline_SRT()
        self.__extract_dialogues_SRT()

        # for store new timelines
        new_timelines = []        

        # split gap to minutes and seconds
        mins = int(gap.split()[0])
        sec = float(gap.split()[1])

        if not fwd:
            mins = -mins
            sec = -sec

        # loop through the timeline
        for timeline in self.__timelinesSRT:
            # split each timeline into hours, minutes, seconds
            splitted_time = self.__timelineRegex.findall(timeline)

            seconds1 = float('.'.join((splitted_time[0][2],splitted_time[0][3])))
            seconds2 = float('.'.join((splitted_time[0][-2],splitted_time[0][-1])))

            minutes1 = int(splitted_time[0][1])
            minutes2 = int(splitted_time[0][-3])

            hours1 = int(splitted_time[0][0])
            hours2 = int(splitted_time[0][-4])

            # add seconds
            seconds1 += sec
            seconds2 += sec 

            # checking seconds range
            if seconds1 > 59.999:
                seconds1 = 00.000
                minutes1 += 1
            elif seconds1 < 0:
                seconds1 += 60
                minutes1 -= 1

            if seconds2 > 59.999:
                seconds2 = 00.000
                minutes2 += 1
            elif seconds2 < 0:
                seconds2 += 60
                minutes2 -= 1

            # add minutes
            minutes1 += mins
            minutes2 += mins

            # checking minutes range
            if minutes1 > 59:
                minutes1 = 00
                hours1 += 1
            elif minutes1 < 0:
                minutes1 += 60
                hours1 -= 1

            # !!!! BUG HERE !!!! --> time goes to minus values
            if hours1 < 0:
                seconds1, minutes1, hours1 = 00.000, 00, 00

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

        self.__write_to_srt(new_timelines)
             
    # convert srt file to ssa file
    def srt2ssa(self):
        self.__splitt_SRT()
        self.__extract_timeline_SRT()
        self.__extract_dialogues_SRT()

        

        self.__write_to_ssa()
        

    def ssa2srt(self):
        pass

    @staticmethod
    def initialize(subPath):
        try:
            with open(subPath, 'r+', encoding='utf8') as sub:
                content = sub.read()
            return SubMagic(subPath)
 
        except Exception as e:     # !!!! BUG HERE !!!! --> Should raise an Exception
            print(f'Error - {e}\n')
            return False


if __name__ == "__main__":
    from art import tprint

    
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
    
    except Exception as e:
        print(e)
        
