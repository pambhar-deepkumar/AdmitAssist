import json
import os

import openai
import streamlit as st

from utils.assessment_manager import AssessmentManager
from utils.enums import TestResult
from utils.markdown_parser import MarkdownLLMHelper

from .agents import CourseAssistant, EvaluationAssistant
from .base_strategy import BaseEvaluationStrategy


class ComprehensiveStrategy(BaseEvaluationStrategy):
    def __init__(self):
        super().__init__("Comprehensive Strategy")
        print("Initializing ComprehensiveStrategy")

    def evaluate(self, documents):
        try:
            print("Evaluating application with comprehensive strategy...")
            parser = MarkdownLLMHelper(documents["module_description"])
            manager = AssessmentManager(
                r"data/course_requirements/Assessment Format.json",
                documents["curriculum_analysis"],
            )

            courseAssist = CourseAssistant(parser._markdown_text)
            evaluationAssist = EvaluationAssistant()
            for module in manager:
                eval_one_module = False
                with st.status(
                    f"Processing Module: {module.name}", expanded=True
                ) as status:
                    for matchingModule in module:
                        st.text(f"> Retrieving information for {matchingModule.name}")
                        if matchingModule.name:
                            if not eval_one_module:
                                eval_one_module = True
                            print(
                                f"Searching for the {matchingModule.name} in module description"
                            )

                        # Fuzzly searches only in the headers
                        results = parser.fuzzy_match_heading_and_retrieve_lines(
                            keyword=matchingModule.name,
                            num_lines=100,
                            ratio_threshold=0.7,
                        )
                        if not results:
                            # Matching exact sequence over all document and return 150 lines after search
                            results = parser.fuzzy_search_with_lines(
                                keyword=matchingModule.name,
                                num_lines=150,
                                ratio_threshold=1,
                            )
                            if not results:
                                # pass full document and course name for extraction
                                extractedResult = self.extractInfoFullDocs(
                                    assistance=courseAssist,
                                    moduleName=matchingModule.name,
                                )
                            else:
                                extractedResult = self.extractInfoContent(
                                    moduleName=matchingModule.name,
                                    content=results["content"],
                                )
                        else:
                            extractedResult = self.extractInfoContent(
                                moduleName=matchingModule.name,
                                content=results["content"],
                            )
                            result = self.extract_json_by_braces(extractedResult)
                            if (
                                result["course_name"] == "null"
                                or result["course_name"] == None
                            ):
                                extractedResult = self.extractInfoFullDocs(
                                    assistance=courseAssist,
                                    moduleName=matchingModule.name,
                                )

                        required = {
                            "Module Name": module.name,
                            "Module Content": module.content,
                            "Module Learning Outcome": module.learnOut,
                        }
                        st.text(
                            "> Matching the extracted information with the required information"
                        )
                        unparsedResult = self.evaluateCourse(
                            evaluationAssist, extractedResult, required
                        )
                        evaluationResult = self.extract_json_by_braces(unparsedResult)
                        if evaluationResult == None or evaluationResult == "null":
                            matchingModule.set_evaluation(
                                TestResult.NOT_FOUND,
                                "> No evaluation result found while parsing",
                            )
                        elif (
                            evaluationResult["judgement"] == "null"
                            or evaluationResult["judgement"] == None
                            or evaluationResult["judgement"] == "Null"
                        ):
                            st.warning(
                                f"> Module {matchingModule.name} evaluation not found."
                            )
                            matchingModule.set_evaluation(
                                TestResult.NOT_FOUND, evaluationResult["reason"]
                            )
                        elif (
                            evaluationResult["judgement"] == True
                            or evaluationResult["judgement"] == "True"
                            or evaluationResult["judgement"] == "true"
                        ):
                            st.success(
                                f"> Module {matchingModule.name} evaluation passed.\n Feedback: {evaluationResult['reason']}"
                            )
                            matchingModule.set_evaluation(
                                TestResult.PASSED, evaluationResult["reason"]
                            )
                        elif (
                            ~evaluationResult["judgement"]
                            or evaluationResult["judgement"] == "False"
                            or evaluationResult["judgement"] == "false"
                        ):
                            st.error(
                                f"> Module {matchingModule.name} evaluation failed.\n Feedback: {evaluationResult['reason']}"
                            )
                            matchingModule.set_evaluation(
                                TestResult.NOT_PASSED, evaluationResult["reason"]
                            )
                        else:
                            st.warning(
                                f"> Module {matchingModule.name} evaluation not found."
                            )
                            matchingModule.set_evaluation(
                                TestResult.NOT_FOUND, evaluationResult["reason"]
                            )

                    if not eval_one_module:
                        st.error(
                            f"No incoming modules for module {module.name} in curriculum anlysis. Please try again."
                        )
                    status.update(
                        label=f"Module {module.name} evaluation.", expanded=False
                    )

            return True, manager.get_wb()

        except Exception as e:
            st.error(
                f"An error occurred during evaluating module:{module}. Please try again."
            )
            st.exception(e)
            return False, None

    def extract_json_by_braces(self, text):
        """
        Extracts the JSON substring from the first pair of matching curly braces
        and returns it as a Python dictionary.

        Parameters
        ----------
        text : str
            The string containing the target JSON object.

        Returns
        -------
        dict
            Parsed JSON data as a Python dictionary. If no valid JSON is found,
            returns an empty dictionary.

        Notes
        -----
        - This function uses a stack to match the first opening curly brace '{'
        with its corresponding closing brace '}'.
        - If the content in between is not valid JSON, 'json.JSONDecodeError'
        will be raised or caught.
        """

        stack = []
        start_index = None
        end_index = None

        for i, char in enumerate(text):
            if char == "{":
                # If the stack is empty, mark this as the start of the JSON object.
                if not stack:
                    start_index = i
                stack.append("{")
            elif char == "}":
                if stack:
                    stack.pop()
                    # If the stack is empty, we've found the matching closing brace.
                    if not stack:
                        end_index = i
                        break

        # If we found a matching set of braces, attempt to parse the substring as JSON.
        if start_index is not None and end_index is not None:
            json_str = text[start_index : end_index + 1]

            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")
                return None
        else:
            print("No matching curly braces that define a JSON object were found.")
            return None

    def evaluateCourse(self, evaluationAssist: EvaluationAssistant, result, require):
        prompt = f"""
  ¯              Here is required course format:
                {require}

                 Here is incoming students course format:
                {result}
        """

        return evaluationAssist.compare(prompt)

    def extractInfoFullDocs(self, assistance, moduleName):
        return assistance.ask_question("Input: " + moduleName)

    def extractInfoContent(self, moduleName: str, content: str) -> dict:
        module_description = """| Teaching   | Component                              | Rota   | Attendance   |       | Selfstudy ECTS   |
    |------------|----------------------------------------|--------|--------------|-------|------------------|
    | lecture    | Lecture: Introduction to Programming   | WiSe   | 60 h (4 SWS) | 120 h | 6 CP             |
    | exercise   | Exercises: Introduction to Programming | WiSe   | 30 h (2 SWS) | 60 h  | 3 CP             |
    9 credit points are awarded for this module. The attendance time is 6 hours a week. Including self-study, there are about 270 hours to be spent.
    | Type                  | compulsory module with compulsory module components                                                                                                                                                                                                                                                                                                                                                                                           |
    |-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | Usability             | This module is offered in the following programmes - INF-B-120: Bachelor Programme in Computer Science with 60-CP Minor Subject - INF-B-150: Bachelor Programme in Computer Science with 30-CP Minor Subject - INF-B-180-CL: Bachelor Programme in Computer Science plus Computer Linguistics - INF-B-180-MA: Bachelor Programme in Computer Science plus Mathe- matics - INF-B-180-STAT: Bachelor Programme in Computer Science plus Statis- |
    | Entry Requ.           | none                                                                                                                                                                                                                                                                                                                                                                                                                                          |
    | Time during the study | 1. Semester                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | Duration              | The module comprises 1 semester.                                                                                                                                                                                                                                                                                                                                                                                                              |
    | Grading               | marked                                                                                                                                                                                                                                                                                                                                                                                                                                        |
    | Type of Examination   | Klausur (90-180 Minute) oder mündlich (15-30 Minute) Repeatability: once, next chance, Admission Requirements: none Qualifying Examination (Grundlagen und Orientierungsprüfung), also for INF-B-120, INF-B-150, INF-B-180-CL, INF-B-180-MA, INF-NF-15, MINF- B-180                                                                                                                                                                           |
    | Responsible for Module   | Prof. Dr. Hans Jürgen Ohlbach                                                           |
    |--------------------------|-----------------------------------------------------------------------------------------|
    | Provider                 | Ludwig-Maximilians-University Munich                                                    |
    |                          | Faculty for Mathematics, Computer Science and Statistics Institute for Computer Science |
    Lang.
    This module provides an introduction to the imperative, object-oriented and concurrent programming using a high level language, e.g. Java. In addition to the knowledge of general programming principles, concepts, methods and techniques for displaying, structuring and processing of data and the development of algorithms are discussed. Particular emphasis is set on conceptual clarity and precise mathematical foundation with formal methods.
    The main topics of the course are as follows:
    · basic concepts about programs and their implementation;
    · syntax of programming languages and their description;
    · basic data types and imperative control structures;
    · complexity and correctness of imperative programs;
    · recursion;
    · simple sorting methods;
    · introduction to the object-oriented program design;
    · classes, interfaces and packages;
    · inheritance, and exception handling;
    · object-oriented implementation of lists and tree structures;
    · basic concepts of concurrent programming: threads, synchronization and deadlock,
    · Introduction to UML-Diagrams,
    · Programming with an Integrated Development Environment (currently Eclipse).
    There is a multitude of introductory books about Computer Science and Java in particular. A comprehensive Java book, which is also online available, is:
    · Java ist auch eine Insel, von Christian Ullenboom, Gilileo Computing, ISBN = 978-3-83621802-3
    An easier introductory book is
    · Java kompakt, von Hözl, Read und Wirsing, Springer Vieweg, ISBN 978-3-642-28503-5
    The module consists of a lecture and in addition exercises in small groups. The concepts introduced in the lecture are practiced in the exercise class with concrete examples.
    German
    The students will be able to implement solutions for small and manageable problems algorithmically and to realize them with a high level programming language as executable programs. Using an IDE like Eclipse facilitates the professionalisation. Furthermore, students develop an understanding of the general principles of programming and programming languages. This lays the foundation to ensure that the students (after further experiences in the course of study) may become familiar quickly and accurately with any programming language.
    | Teaching   | Component                                                     | Rota   | Attendance   |       | Selfstudy ECTS   |
    |------------|---------------------------------------------------------------|--------|--------------|-------|------------------|
    | lecture    | Lecture: Analysis for Computer Scientists and Statisticians   | WiSe   | 60 h (4 SWS) | 120 h | 6 CP             |
    | exercise   | Exercises: Analysis for Computer Scientists and Statisticians | WiSe   | 30 h (2 SWS) | 60 h  | 3 CP             |
    9 credit points are awarded for this module. The attendance time is 6 hours a week. Including self-study, there are about 270 hours to be spent.
    | Type                   | compulsory module with compulsory module components                                                                                                                                                                                                                                                                                               |
    |------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | Usability              | This module is offered in the following programmes - INF-B-150: Bachelor Programme in Computer Science with 30-CP Minor Subject - INF-B-180-CL: Bachelor Programme in Computer Science plus Computer Linguistics - INF-B-180-STAT: Bachelor Programme in Computer Science plus Statis- tics - MINF-B-180: Bachelor Programme in Media Informatics |
    | Entry Requ.            | none                                                                                                                                                                                                                                                                                                                                              |
    | Time during the study  | 1. Semester                                                                                                                                                                                                                                                                                                                                       |
    | Duration               | The module comprises 1 semester.                                                                                                                                                                                                                                                                                                                  |
    | Grading                | marked                                                                                                                                                                                                                                                                                                                                            |
    | Type of Examination    | Klausur (90-180 Minute) oder mündlich (15-45 Minute) Repeatability: arbitrary, Admission Requirements: none                                                                                                                                                                                                                                       |
    | Responsible for Module | Prof. Dr. Heinz Siedentop                                                                                                                                                                                                                                                                                                                         |
    | Provider               | Ludwig-Maximilians-University Munich Faculty for Mathematics, Computer Science and Statistics Department of Mathematics                                                                                                                                                                                                                           |
    | Teaching Lang.         | German                                                                                                                                                                                                                                                                                                                                            |
    The module gives a hands-on introduction into analysis and its applications. The main focus is on the development of mathematical methods and insights. It introduces sets, relations, mappings, induction, recursive definitions, real numbers, sequences and series, power series, continuous and differentiable functions in one and many variables, complex numbers, norms, and metrics.
    The module consists of a lecture and in addition exercises in small groups. The concepts introduced in the lecture are practiced in the exercise class with concrete examples.
    The basic parts of Analysis are to be understood. Mathematical methods and ways of thinking are to be adopted.
    | Teaching   | Component                                         | Rota   | Attendance   |      | Selfstudy ECTS   |
    |------------|---------------------------------------------------|--------|--------------|------|------------------|
    | lecture    | Lecture: Linear Algebra for Computer Scientists   | WiSe   | 45 h (3 SWS) | 75 h | 4 CP             |
    | exercise   | Exercises: Linear Algebra for Computer Scientists | WiSe   | 30 h (2 SWS) | 30 h | 2 CP             |
    6 credit points are awarded for this module. The attendance time is 5 hours a week. Including self-study, there are about 180 hours to be spent.
    | Type                   | compulsory module with compulsory module components                                                                                                                                                                                                                                                                                               |
    |------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | Usability              | This module is offered in the following programmes - INF-B-150: Bachelor Programme in Computer Science with 30-CP Minor Subject - INF-B-180-CL: Bachelor Programme in Computer Science plus Computer Linguistics - INF-B-180-STAT: Bachelor Programme in Computer Science plus Statis- tics - MINF-B-180: Bachelor Programme in Media Informatics |
    | Entry Requ.            | none                                                                                                                                                                                                                                                                                                                                              |
    | Time during the study  | 1. Semester (INF-B-180-STAT, INF-B-150, INF-B-180-CL), 3. Semester (MINF-B-180)                                                                                                                                                                                                                                                                   |
    | Duration               | The module comprises 1 semester.                                                                                                                                                                                                                                                                                                                  |
    | Grading                | marked                                                                                                                                                                                                                                                                                                                                            |
    | Type of Examination    | Klausur (90-180 Minute) oder mündlich (15-45 Minute) Repeatability: arbitrary, Admission Requirements: none                                                                                                                                                                                                                                       |
    | Responsible for Module | Prof. Dr. Andreas Rosenschon                                                                                                                                                                                                                                                                                                                      |
    | Provider               | Ludwig-Maximilians-University Munich Faculty for Mathematics, Computer Science and Statistics Department of Mathematics                                                                                                                                                                                                                           |
    | Teaching               | German                                                                                                                                                                                                                                                                                                                                            |
    Lang.
    The module gives a hands-on introduction to the methods of linear algebra, their applications, and the development of basic algebraic notions. It introduces vectors, real matrices and linear algebra in the R n , abstract linear algebra, determinants, eigenvalues and eigenvectors.
    The module consists of a lecture and in addition exercises in small groups. The concepts introduced in the lecture are practiced in the exercise class with concrete examples.
    The basics of Linear Algebra as well as general mathematical ways of thinking are to be understood and practically applicable.
    Part of: Bachelor Programme in Computer Science plus Statistics (180 CP)
    Associated Module Components:
    | Teaching   | Component                          | Rota   | Attendance   |      | Selfstudy ECTS   |
    |------------|------------------------------------|--------|--------------|------|------------------|
    | lecture    | Descriptive Statistics (lecture)   | WiSe   | 45 h (3 SWS) | 75 h | 4 CP             |
    | exercise   | Descriptive Statistics (exercises) | WiSe   | 15 h (1 SWS) | 45 h | 2 CP             |
    6 credit points are awarded for this module. The attendance time is 4 hours a week. Including self-study, there are about 180 hours to be spent.
    | Type                   | compulsory module with compulsory module components                                                                                                                                                                                                                             |
    |------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | Entry Requ.            | none                                                                                                                                                                                                                                                                            |
    | Time during the study  | 1. Semester                                                                                                                                                                                                                                                                     |
    | Duration               | The module comprises 1 semester.                                                                                                                                                                                                                                                |
    | Grading                | marked                                                                                                                                                                                                                                                                          |
    | Type of Examination    | Klausur (90-180 Minute) oder mündlich (15-30 Minute) oder Hausarbeit (5- 20 Seiten) oder (Klausur (75-150 Minute) und Übungsblätter (15-40 Stun- den)) oder (mündlich (50-105 Minute) und Übungsblätter (15-40 Stunden)) Repeatability: arbitrary, Admission Requirements: none |
    | Responsible for Module | Dr. Helmut Küchenhoff                                                                                                                                                                                                                                                           |
    | Provider               | Ludwig-Maximilians-University Munich Faculty for Mathematics, Computer Science and Statistics Department of Statistics                                                                                                                                                          |
    | Teaching Lang.         | German                                                                                                                                                                                                                                                                          |
    This module introduces to descriptive statistics. It starts by discussing methods to describe and characterize univariate frequency distributions. Then the basic descriptive techniques for multivariate data are developed and different methods to measure association and correlation
    are introduced and an introduction to linear regression modelling is given. Basics on stitistical graphics are presented. Furthermore, basics of the practical data analysis are presented. Basic concepts of using selected statistical software packages are presented. First small practical data anaylsis projects are conducted.
    The lecture develops central concepts and methods of descriptive Statistics. Important properties of the main techniques are formulated and illustrated via selected examples. The students shall become proficient with the fundamental methods of descriptive Statistics.
    The exercise classes will deepen the contents of the lecture by applying it to exercises and small projects. The exercise classes shall deepen the understanding of the concepts taught in the lecture and shall enable the students to apply and implement the methods and techniques taught in the lecture.
    """

        prompt = f"""You are analyzing a course module from a university's course catalog. You will be provide an input which is name of the course/module. It can be incomplete or half or missing module codes something and Your task is to retrieve the exact full name of the course with their codes,exact course description/content/syllabus and exact Learning Outcome/Qualification Aim/Aim from the given text. If you do not found that you have to produce None as ouput.
        Here is the format of the conversation:
        Input: Course name
        Content: Content from which you have to search
        Output format: JSON
        Output:
        {{
            "course_name": "String",
            "description": "String",
            "learning_outcomes": "String"
        }}
        Here is an Example for you:
        Input :  P1: Introduction to Programming (INF-EiP)
        Content :{module_description}
        Output :
        {{
            "course_name": "2.1 P 1: Introduction to Programming (INF-EiP)",
            "description": "This module provides an introduction to the imperative, object-oriented and concurrent programming using a high level language, e.g. Java. In addition to the knowledge of general programming principles, concepts, methods and techniques for displaying, structuring and processing of data and the development of algorithms are discussed. Particular emphasis is set on conceptual clarity and precise mathematical foundation with formal methods. The main topics of the course are as follows: basic concepts about programs and their implementation; syntax of programming languages and their description; basic data types and imperative control structures; complexity and correctness of imperative programs; recursion; simple sorting methods; introduction to the object-oriented program design; classes, interfaces and packages; inheritance, and exception handling; object-oriented implementation of lists and tree structures; basic concepts of concurrent programming: threads, synchronization and deadlock; Introduction to UML-Diagrams; Programming with an Integrated Development Environment (currently Eclipse).",
            "learning_outcomes": "The students will be able to implement solutions for small and manageable problems algorithmically and to realize them with a high level programming language as executable programs. Using an IDE like Eclipse facilitates the professionalisation. Furthermore, students develop an understanding of the general principles of programming and programming languages. This lays the foundation to ensure that the students (after further experiences in the course of study) may become familiar quickly and accurately with any programming language."
        }}
        If you are not able to find that!!
        Output :
        If the course is not found, respond with:
        {{
            "course_name": null,
            "description": null,
            "learning_outcomes": null
        }}

        Extract the full course/module name, course/module description and qualification aim/learning outcomes from the following module description:
        Input: {moduleName}
        Content: {content}
        Output:
        """

        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts specific information from module descriptions.",
                    },
                    {"role": "user", "content": prompt},
                ],
                n=1,
                temperature=0,
            )
            assistanceResponse = response.choices[0].message.content

            print("Here is the extracted result:\n" + assistanceResponse)

            if "None" in assistanceResponse or not assistanceResponse:
                return {"response": "None"}
            else:
                return assistanceResponse
        except Exception as e:
            return f"An error occurred: {str(e)}"
