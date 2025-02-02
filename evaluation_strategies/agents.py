import json
import os

import openai


class CourseAssistant:
    def __init__(self, course_catalog):
        self.course_catalog = course_catalog
        self.client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.messages = [{"role": "system", "content": self.get_system_message()}]

    def get_system_message(self):
        return f"""You are analyzing a course module from a university's course catalog. You will be provided an input which is the name of the course/module and the whole university course catalog. Your task is to retrieve the exact course description/content/syllabus and exact Learning Outcome/Qualification Aim/Aim from the given course catalog for the given course name. If you do not find that, you have to produce None as output.
                Here is the course Catalog:
                {json.dumps(self.course_catalog, indent=2)}

                Please respond in JSON format as follows:
                {{
                    "course_name": "String",
                    "description": "String",
                    "learning_outcomes": "String"
                }}

                If the course is not found, respond with:
                {{
                    "course_name": null,
                    "description": null,
                    "learning_outcomes": null
                }}

                for example -
                Here is an Example for you:
                Input : Introduction to Programming (INF-EiP)
                Output :
                {{
                    "course_name": "2.1 P 1: Introduction to Programming (INF-EiP)",
                    "description": "This module provides an introduction to the imperative, object-oriented and concurrent programming using a high level language, e.g. Java. In addition to the knowledge of general programming principles, concepts, methods and techniques for displaying, structuring and processing of data and the development of algorithms are discussed. Particular emphasis is set on conceptual clarity and precise mathematical foundation with formal methods. The main topics of the course are as follows: basic concepts about programs and their implementation; syntax of programming languages and their description; basic data types and imperative control structures; complexity and correctness of imperative programs; recursion; simple sorting methods; introduction to the object-oriented program design; classes, interfaces and packages; inheritance, and exception handling; object-oriented implementation of lists and tree structures; basic concepts of concurrent programming: threads, synchronization and deadlock; Introduction to UML-Diagrams; Programming with an Integrated Development Environment (currently Eclipse).",
                    "learning_outcomes": "The students will be able to implement solutions for small and manageable problems algorithmically and to realize them with a high level programming language as executable programs. Using an IDE like Eclipse facilitates the professionalisation. Furthermore, students develop an understanding of the general principles of programming and programming languages. This lays the foundation to ensure that the students (after further experiences in the course of study) may become familiar quickly and accurately with any programming language."
                }}

            """

    def ask_question(self, question):
        self.messages.append({"role": "user", "content": question})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.messages,
                temperature=0,
            )

            assistant_response = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_response})

            print("Here is the extracted result:\n" + assistant_response)
            return assistant_response

        except Exception as e:
            return f"An error occurred: {str(e)}"


class EvaluationAssistant:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.messages = [{"role": "system", "content": self.get_system_message()}]

    def get_system_message(self):
        return f"""You are a university course coordinator. Your job is analyzing and comparing 2 course module from two different university. Your task is to compare that these two course are matching or not. You have to look at the course content/syllabus/discription from both course and also try to understand the learning outcome/Qualification Aim/Goal of both course. At the end you have to produce a reason behind your judgement. If it is matching provide why do you think that and if it is not matching produce why it is not matching. Please provide reason not more than 100 words.
                INPUT:
                Here is required course format:
                {{
                    "Module Name": Name of the Course,
                    "Module Content": Description of the Course,
                    "Module Learning Outcome": Learning Outcome of the Course,
                }}

                Here is incoming students course format:
                {{
                    "course_name": Name of the Course,
                    "description": Description of the Course,
                    "learning_outcomes": Learning Outcome of the Course,
                }}

                OUTPUT:
                {{
                    "judgement": true/false,
                    "confidence" : Generate a score how confident you are (0-100),
                    "reason" : Generate a reason not more than 100 words,

                }}

                If one of course description is null or If you are not able to make a judgement then please produce following output with suitable reason
                OUTPUT:
                {{
                    "judgement": null,
                    "confidence" : null,
                    "reason" :  Generate a reason not more than 100 words,

                }}

            """

    def compare(self, question):
        self.messages.append({"role": "user", "content": question})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.messages,
                temperature=0,
            )

            assistant_response = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_response})

            print(
                "Here is the Judgement from the LLM with the reason"
                + assistant_response
            )
            return assistant_response

        except Exception as e:
            return f"An error occurred: {str(e)}"
