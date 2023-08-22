import subprocess

class Bito(object):
    def __init__(self) -> None:
        self.cli: str = "bito"
        
    def shrink_news_file(self, input_file_path: str, output_file_path: str) -> None:
        """
        :param input_file: Path to file with initial news
        :param output_file: Path to file to append modified news 
        """
        input_file = open(input_file_path, 'r')
                
        for input_line in input_file:
            input_line: str = input_line.strip()  
            modified_line: str = self.shrink_news(input_line)
            with open(output_file_path, 'a') as output_file:
                output_file.write(modified_line + '\n')
        
        input_file.close()
        

    def shrink_news(self, input_str: str) -> str:
        """
        :param input_str: String with news to modify
        
        :return: News modified by AI
        """
        task: str = "Ответь на русском языке в одну строку. Сократи текст до 5 предложений выделить главные мысли:\n"
        input_str = task + input_str
        
        output: str = self.get_cli_answer(input_str)
        
        return output


    def get_cli_answer(self, input_str: str) -> str:
        """
        :input_str: String to be sent to cli
        
        :return: Answer from cli
        """
        # Start the CLI application as a subprocess
        process = subprocess.Popen(self.cli, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

        # Pass the input to the CLI application
        process.stdin.write(input_str.encode())

        # Read the output from the CLI application
        output, _ = process.communicate()
        output = output.decode().strip()

        # Close the subprocess
        process.stdin.close()
        process.stdout.close()
        process.wait()

        # Return the output
        return output


if __name__ == '__main__':
    pass