import re
import pyperclip

# Define a custom object to store the required information
class ActionData:
    def __init__(self, sequence_tag, hour, mention, minute,id,timestamp,content):
        self.sequence_tag = sequence_tag
        self.hour = hour
        self.minute = minute
        self.id=id
        self.endtime=timestamp
        self.duration="00min"
        self.mention=mention
        self.timestamp=timestamp
        self.content=content
        self.string=None
    
    def setString(self):
        if(self.hour==0):
            if self.mention=="":
                self.string= f"{self.id}) {self.sequence_tag} | {self.timestamp}-{self.endtime} | {self.duration}"
            else:
                self.string= f"{self.id}) {self.sequence_tag} | {self.mention} | {self.timestamp}-{self.endtime} | {self.duration}"
        else:
            if self.mention=="":
                self.string= f"{self.id}) {self.sequence_tag} | {self.timestamp}-{self.endtime} | {self.duration}"
            else:
                self.string= f"{self.id}) {self.sequence_tag} | {self.mention} | {self.timestamp}-{self.endtime} | {self.duration}"
                
    def setEndingTime(self,nexttime,endhour,endminute):
        
        try:
            self.endtime=nexttime
            duration=endhour*60+endminute-self.hour*60-self.minute
            
            hr = int(duration/60)
            min = int(duration%60)
            # Ensure hr and min are valid integers
            if hr is None or min is None:
                raise ValueError("hr or min is None")
            
            # Format the duration string based on hr and min values
            self.duration = (f"{hr}hr " if hr > 0 else "") + (f"{min:02d}min" if min >= 0 else "")
        except Exception as e:
            print(f"Error calculating duration: {str(e)}")
            self.duration = "error"

        
    def __repr__(self):
        return f"{self.id}) {self.sequence_tag}, {self.hour}hr{self.minute}min"

class ReportGenerator:
    def __init__(self,text):
        super().__init__()
        
        # List of tags to look for
        self.tags = {
            "Interaction", "Recording Ends","Recording ends",
            "Short break", "Short Break","Short Break Initiated","Short Break initiated", 
            "Short break initiated", "Short Break Starts", "Short Break starts",
            "Short break starts","Short Break Ends","Short Break Over", 
            "Short Break Ensues", "Short Break ensues", "Short break ensues",
            "Main Teaching","Main teaching", "Exercise",
            "Live Demonstration", "Live demonstration","Story", "Screen Share",
            "Breakout Rooms Instructions","Breakout Rooms instructions","Breakout rooms instructions",
            "Breakout Rooms Instruction","Breakout Rooms instruction", "Breakout rooms instruction",
            "Breakout Room Instructions","Breakout Room instructions","Breakout room instructions",
            "Breakout Room Initiated","Breakout Room End", "Breakout Room end", "Breakout room end",
            "Breakout room initiated", "Breakout Room initiated",
            "Breakout Rooms Ensue","Breakout Rooms ensue","Breakout rooms ensue",
            "Breakout Room Ensue","Breakout Room ensue","Breakout room ensue",
            "Breakout Room Ensues","Breakout Room ensues","Breakout room ensues",
            "Breakout Rooms Starts","Breakout Rooms starts","Breakout rooms starts",
            "Breakout Room Starts","Breakout Room starts","Breakout room starts",
            "Breakout Rooms Start","Breakout Rooms start","Breakout rooms start",
            "Breakout Room Start","Breakout Room start","Breakout room start",
            "Breakout Rooms Dissolved","Breakout Rooms dissolved","Breakout rooms dissolved",
            "Breakout Room Dissolved","Breakout Room dissolved","Breakout room dissolved",
            "Breakout Rooms Initiated","Breakout Rooms End", "Breakout Rooms end", "Breakout rooms end",
            "Breakout rooms initiated", "Breakout Rooms initiated",
            "Breakout Rooms Ends", "Breakout Rooms ends", "Breakout rooms ends",
            "Breakout Room Ends", "Breakout Room ends", "Breakout room ends",
            "Share", "Question", "Recording Starts","Recording starts", "Recording Stops", "Recording Stopped", "Recording stops",
            "Recording ends","Recording Ends","Recording stopped",
            "Session ends","Session Ends"
        }
        
        # Regular expressions to extract components
        self.duration_pattern = r"\((?:(\d{1,2})hr)?(\d{1,2})min\)"# Updated regular expression to handle both (03hr36min) and (00min)
        # Updated regular expression to handle durations like 1hr23min, 3hr59min, 00min, etc.
        #self.duration_pattern = r"\((?:(\d{1,2})hr)?(\d{1,2})min\)"
        self.timestamp_pattern = r"\*(\d{1,2}):(\d{2})\s*(am|pm)\*"
        self.mention_pattern = r'\(Trainer:\s*([^)]*?)(?:,\s*Delegate:\s*([^)]*?))?\)|\(Delegate:\s*([^)]*?)\)'
        self.tag_pattern = r"(" + "|".join(re.escape(tag) for tag in self.tags) + r")[\:.]"
        #self.music_pattern = r"\. Music:\s*(.+?)\."
        #self.music_pattern = r"Music:\s*(.+?)\."
        self.music_pattern = r"Music:\s*(.+?)(?:\.|\n)"

        # Initialize a list to store EventData objects
        self.event_data_list = []

        # Variable to hold the most recent duration
        self.last_known_hour = None
        self.last_known_minute = None
        self.prevtime= int(14),int(30)

        # Initialize first id to zero
        self.id=0
        
        # Initialize text
        self.text = text
     
    def title_line(self):
        """Extract the first line, convert it to uppercase, and append it back to the original text."""
        lines = self.text.splitlines()
        first_line=""
        if lines:
            # Extract the first line and convert it to uppercase
            first_line = lines[0].upper()
            first_line=first_line.strip()
            if "TIMESTAMPS, " in first_line:
                first_line = first_line.replace("TIMESTAMPS, ", "")
        
        return first_line
        
    def extract_time(self, line):
        timestamp_re = re.compile(self.timestamp_pattern)
        match = timestamp_re.search(line)
        if match:
            hour, minute, period = int(match.group(1)), int(match.group(2)), match.group(3)
            if period == 'pm' and hour != 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
            self.prevtime=hour,minute
            return hour, minute
        else:
            return self.prevtime
    
    def extract_content(self,line):
        # Remove all patterns from the line
        line = re.sub(self.duration_pattern, '', line)
        line = re.sub(self.timestamp_pattern, '', line)
        line = re.sub(self.mention_pattern, '', line)
        line = re.sub(self.tag_pattern, '', line)
        return line.strip()
            
    def extract_mentions(self,line):
        text=""
        mentions = {}        
        # Split the text into lines and iterate through each line
        match = re.search(self.mention_pattern, line)
        if match:
            trainer = match.group(1).strip() if match.group(1) else None
            delegate = match.group(2).strip() if match.group(2) else match.group(3).strip() if match.group(3) else None
            mentions={'trainer': trainer, 'delegate': delegate}
        
        
        if mentions=={}:
            text=""
        elif mentions['trainer'] == None:
            text= (f"Delegate - {mentions['delegate']}")
        elif mentions['delegate'] == None:
            text= (f"Trainer - {mentions['trainer']}")
        else:
            text= (f"Trainer - {mentions['trainer']}, Delegate - {mentions['delegate']}")
        return text
    
    
    def extract_music(self):
        music_matches = re.findall(self.music_pattern, self.text)
        #print(music_matches)
        return tuple(music_matches)
    
    
    def remove_empty_lines(self,text):
        """Remove empty lines from the input text."""
        lines = text.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        return '\n'.join(non_empty_lines)
    
    def extract_and_copy(self):
        
        self.text=self.remove_empty_lines(self.text)
        self.lines=self.text.split('\n')
        firstaction=True
        # Iterate through each line and extract duration and tag
        output_string=""
        for line in self.lines:
            content=self.extract_content(line)
            time=self.extract_time(line)
            timestamp=str(time[0])+":"+(str(time[1]) if time[1]>9 else ("0"+str(time[1])))+ (" am" if time[0]<12 else " pm")
            
            mention=self.extract_mentions(line)
            duration_match = re.search(self.duration_pattern, line)
            tag_match = re.search(self.tag_pattern, line)
            
            # If a duration is found, update the last known duration
            if duration_match:
                self.last_known_hour =  int(duration_match.group(1)) if duration_match.group(1) else 0
                self.last_known_minute = int(duration_match.group(2))
            
            if(firstaction==True):
                firstaction=False
            else:
                for event in self.event_data_list:
                    if event.id==self.id:
                        event.setEndingTime(timestamp,self.last_known_hour,self.last_known_minute)
                        event.setString()         
            
            # If a tag is found, create an EventData object
            if tag_match:
                self.id=self.id+1
                tag = tag_match.group(1)
                
                # Use the last known duration if no new duration is found
                
                event_data = ActionData(sequence_tag=tag, hour=self.last_known_hour, minute=self.last_known_minute,id=self.id,mention=mention,timestamp=timestamp, content=content)
                self.event_data_list.append(event_data)
         
        for event in self.event_data_list:
            if event.id==self.id:
                event.setString()
                
        # Compile the output into a single string
        for event in self.event_data_list:
            string=event.string
            output_string=output_string+string+'\n\n'
            
        return output_string
    
    def fullReport(self):
        report="*REPORT:* "+self.title_line()+"\n\n\n"
        music=self.extract_music()
        i=1
        for song in music:
            report += "Music "+str(i)+": " + song + "\n"
            i=i+1
        closingaction = self.event_data_list[-1]
        report+="\nDuration: "+str(closingaction.hour)+"hr"+str(closingaction.minute)+"min\n\n"
        report+=self.topics()+self.generateReport("Breakout Rooms Instructions")+self.generateReport("Question")+self.generateReport("Live Demonstration")+self.generateReport("Exercise")+self.generateReport("Short Break")+self.generateReport("Screen Share")
        pyperclip.copy(report)
        
    
    
    def generateReport(self,tag="Live Demonstration"):
        report=""
        seperator="-"*40+"\n\n\n"
        report=report+seperator
        srtag={"Short break", "Short Break","Short Break Initiated","Short Break initiated", "Short break initiated", "Short Break Starts", "Short Break starts",
               "Short break ensues","Short Break Ensues","Short Break ensues","Short break starts"}
        brtag={"Breakout Rooms Instructions","Breakout Rooms instructions","Breakout rooms instructions","Breakout Rooms Instruction","Breakout Rooms instruction",
            "Breakout rooms instruction","Breakout Room Instruction","Breakout Room instruction",
            "Breakout room instruction",
            "Breakout Room Instructions","Breakout Room instructions","Breakout room instructions"}
        if tag in brtag :
            report+="BREAKOUT ROOMS\n\n"
            tag=brtag.copy()
        elif tag in srtag :
            report+="SHORT BREAKS\n\n"
            tag=srtag.copy()
        else:
            report+=tag.upper()+"\n\n"
        id=1
        br=0
        for idx, event in enumerate(self.event_data_list):
            if event.sequence_tag in tag:
                if(tag=="Screen Share" and event.sequence_tag=="Share"):
                    pass
                else:
                    if(event.sequence_tag in brtag):
                        br=idx
                        event = self.event_data_list[br+1]
                        while br+1 < len(self.event_data_list) and ("Breakout Room" not in event.sequence_tag and "Breakout room" not in event.sequence_tag):
                            event = self.event_data_list[br+1]
                            br += 1
                    if(event.mention==""):
                        report=report+str(id)+") "+event.duration+", "+event.timestamp+"-"+event.endtime+"\n"
                    else:
                        report=report+str(id)+") "+event.mention+", "+event.duration+", "+event.timestamp+"-"+event.endtime+"\n"
                    id=id+1
                
        if(id==1):
            return ""
        id=1
        report=report+"\n\nContent:\n\n"
        for event in self.event_data_list:
            if event.sequence_tag in tag:
                if(tag=="Screen Share" and event.sequence_tag=="Share"):
                    pass
                else:
                    report=report+str(id)+") "+event.content+"\n\n"
                    id=id+1
        return(report)    
    
    def extract_minutes(self,time_str):
        # Define the regular expression pattern to capture hours and minutes
        pattern = r"(?:(\d+)hr\s*)?(\d+)min"
        
        # Search for the pattern in the input string
        match = re.search(pattern, time_str)
        
        if match:
            hours = int(match.group(1)) if match.group(1) else 0  # Default to 0 if no hours
            minutes = int(match.group(2))
            total_minutes = hours * 60 + minutes
            return total_minutes
        else:
            return None  # In case the string doesn't match the pattern

    
    def topics(self):
        tags = {
            "Short break", "Short Break","Short Break Initiated","Short Break initiated", "Short break initiated", "Short Break Starts", "Short Break starts",
               "Short break starts", "Exercise",
            "Live Demonstration", "Screen Share",
            "Breakout Rooms Instructions","Breakout Rooms instructions","Breakout rooms instructions","Breakout Rooms Instruction","Breakout Rooms instruction"
            "Breakout rooms instruction",
            "Breakout Room Instructions","Breakout Room instructions","Breakout room instructions"
        }
        brtag={"Breakout Rooms Instructions","Breakout Rooms instructions","Breakout rooms instructions","Breakout Rooms Instruction","Breakout Rooms instruction"
            "Breakout rooms instruction",
            "Breakout Room Instructions","Breakout Room instructions","Breakout room instructions"
        }
        srtag={"Short break", "Short Break","Short Break Initiated","Short Break initiated", "Short break initiated", "Short Break Starts", "Short Break starts",
               "Short break starts"}
        report=""
        seperator="-"*40+"\n\n\n"
        report=report+seperator
        report+="TOPICS COVERED\n\n"
        id=1
        br=0
        totalduration=5
        totalhr=0
        totalmin=5
        hr=0
        min=0
        losthr=0
        lostmin=0
        lost=0
        bno=0
        durevent=None
        
        report=report+str(id)+") "+("*"+"Introductions"+"*") +" ("+"5min"+")"+"\n"
        id=id+1
        
        for idx, event in enumerate(self.event_data_list):
            tag=event.sequence_tag
            if tag in  tags:
                if(tag in brtag):
                    losttime=totalhr*60+totalmin-losthr*60-lostmin
                    hr=int(losttime/60)
                    min=losttime%60
                    report+=str(id)+") _*Total Time Taken: "+(str(hr)+"hr" if hr>0 else "")+str(min)+"min*_\n\n"
                    losthr+=hr
                    lostmin+=min
                    id+=1
                    bno+=1
                    tag="Breakout Room "+str(bno)
                if(tag in srtag):
                    losttime=totalhr*60+totalmin-losthr*60-lostmin
                    hr=int(losttime/60)
                    min=losttime%60
                    report+=str(id)+") _*Total Time Taken: "+(str(hr)+"hr" if hr>0 else "")+str(min)+"min*_\n\n"
                    lost=self.extract_minutes(event.duration)
                    losthr+=hr+int(lost/60)
                    lostmin+=min+int(lost%60)
                    id+=1
                durevent=event
                br=idx
                while(durevent.duration=="00min" and br+1 < len(self.event_data_list)):
                    durevent=self.event_data_list[br+1]
                    br+=1
                if(event.sequence_tag in brtag):
                    br=idx
                    durevent = self.event_data_list[br+1]
                    while br+1 < len(self.event_data_list) and ("Breakout Room" not in durevent.sequence_tag and "Breakout room" not in durevent.sequence_tag):
                        durevent = self.event_data_list[br+1]
                        br += 1
                    lost=self.extract_minutes(durevent.duration)
                    losthr+=int(lost/60)
                    lostmin+=int(lost%60)
                  
                report=report+str(id)+") "+(("*"+tag+"*") if "Screen Shar" not in tag else "")+(": " if "Screen Shar" not in tag and "Short Break" not in tag else "")+((event.content.split('.')[0]) if "Short Break" not in tag else "")+" ("+durevent.duration+")"+"\n"
                id=id+1
                if(event.sequence_tag in brtag):
                    report+=str(id)+") "+"Breakout Room Debrief (min)\n"
                    id=id+1
                totalduration+=self.extract_minutes(durevent.duration)
                totalhr=int(totalduration/60)
                totalmin=totalduration%60
        report+=str(id)+") _*Total Time Taken: "+str(totalhr)+"hr"+str(totalmin)+"min*_\n\n"+seperator
        return(report)    
        


# Driver Function for testing
if __name__== "__main__":
    # Sample string
    text = """
    *06:00 pm* (18min) Recording Starts. Music: hello how are you. 
    *06:08 pm* (26min) Live Demonstration: Now that you have this knowledge and wisdom, there is no turning back. Every day, whatever is happening in your body, you’re going to associate it with the meridians. (Trainer: Dr Rangana)
    *06:13 pm* (31min) Screen Share: Liver Meridian Vitaliser, Liver Meridian Cleansing
    Breakout Rooms Instructions: Hi hello guys umma. Music: allalalla.
    *06:18 pm* (36min) Live Demonstration: Who’s ready to work on the liver together? (Trainer: Dr Rangana)
    *07:09 pm* (01hr57min) Screen Share: Liver Meridian Diagram
    *07:09 pm* (01hr57min) Breakout Rooms Initiated. Recording pauses
    *07:59 pm* (02hr47min) Breakout Rooms End. Recording resumes
    *08:53 pm* (03hr41min) Exercise: Liver Meridian Exercise (Delegate: Adrian LIM Peng Ann)
    *09:10 pm* (03hr58min) Live Demonstration: Now that you have this knowledge and wisdom, there is no turning back. Every day, whatever is happening in your body, you’re going to associate it with the meridians. (Trainer: Dr Rangana)
    *09:12 pm* (04hr00min) Session Ends. Music: Jumping Around by Joel Joseph Justin.
    """
    print("Extracted Event Data:")
    ed=ReportGenerator(text)
    print(ed.extract_and_copy())
    ed.fullReport()
   