import re
from collections import Counter


class asteriskdata():
    def __init__(self):
        super().__init__()
        self.modified_string =""
        self.changes_count= 0
        self.partial_asterisks_count= 0
        self.no_asterisks_count= 0
        self.full_asterisks_count= 0
        self.mistakes=[]

class WhatsAppChecker():
    
    def __init__(self):
        super().__init__()

    def find_duplicate_timestamps(self,large_string):
        # Regular expression to match timestamps in the format '01:09 am'
        pattern = r'\b\d{2}:\d{2} [ap]m\b'
        
        # Find all timestamps using the regular expression
        timestamps = re.findall(pattern, large_string)
        
        # Count the occurrences of each timestamp
        timestamp_counts = Counter(timestamps)
        
        # Return the timestamps that appeared more than once
        return [timestamp for timestamp, count in timestamp_counts.items() if count > 1]
    
    def ensure_asterisks_with_tracking(self, large_string):
        # Split the input string into lines
        lines = large_string.splitlines()

        # Pattern to match timestamps with or without partial asterisks
        timestamp_pattern = r'\*?\b\d{1,2}:\d{2}\s?(?:am|pm)\b\*?'

        # Object to store the results
        result = asteriskdata()

        # Function to ensure both asterisks are present
        def ensure_both_asterisks(match):
            timestamp = match.group(0)

            # Case 1: Both asterisks present
            if timestamp.startswith('*') and timestamp.endswith('*'):
                result.full_asterisks_count += 1
                return timestamp  # No change

            # Case 2: Partial asterisks (only one)
            elif timestamp.startswith('*') or timestamp.endswith('*'):
                result.partial_asterisks_count += 1
                clean_timestamp = timestamp.strip('*')
                # If changes were made, update the tracking info
                result.changes_count += 1
                result.mistakes.append(timestamp)
                return f"*{clean_timestamp}*"

            # Case 3: No asterisks at all
            else:
                result.no_asterisks_count += 1
                # If changes were made, update the tracking info
                result.changes_count += 1
                result.mistakes.append(timestamp)
                return f"*{timestamp}*"

        # Process each line
        for i, line in enumerate(lines, start=1):
            # Apply the substitution and count changes
            updated_line,change = re.subn(timestamp_pattern, ensure_both_asterisks, line)

            # Append the modified line to the result
            result.modified_string += updated_line + "\n"

        # Return the object with all required information
        return result


if __name__ == "__main__":
    # Example usage
    large_string = """Meeting at *06:01 am* and again at 12:30 pm.
    Breakfast is at *08:15 am*. 
    Be there at 10:45 am."""
    
    checker = WhatsAppChecker()
    result = checker.ensure_asterisks_with_tracking(large_string)