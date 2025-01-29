class UniversityModule:
    """
    A Python class representing a university module in an academic context,
    with getters and setters to illustrate encapsulation of attributes.

    This class encapsulates three fundamental features of a university module:
        1. The module name
        2. A textual description providing an overview of the subject matter
        3. A summary of learning outcomes that reflect the competencies or
           knowledge students are expected to acquire

    Attributes (accessed via getters and setters):
        module_name (str): Specifies the official or recognized title
            of the module (e.g., "Data Structures and Algorithms").
        description (str): Provides a concise overview of the module's
            academic content, scope, and teaching methodology.
        learning_outcomes (str): Enumerates the expected educational gains,
            detailing specific skills, understandings, or proficiencies
            that students should develop.
    """

    def __init__(
        self, module_name: str, description: str, learning_outcomes: str
    ) -> None:
        """
        Initializes an instance of UniversityModule.

        Args:
            module_name (str): The official name of the module.
            description (str): A high-level summary or abstract of the module's content.
            learning_outcomes (str): A textual statement or list of intended learning outcomes.

        Following object-oriented principles, this constructor stores the provided
        parameters in 'private' attributes (with an underscore prefix), then exposes
        them through carefully managed getters and setters.
        """
        self._module_name = module_name
        self._description = description
        self._learning_outcomes = learning_outcomes

    @property
    def module_name(self) -> str:
        """
        Getter for the module_name attribute.

        Returns:
            str: The current value of the _module_name attribute.

        Encapsulates the retrieval of the module's name, allowing for potential
        future validations or transformations prior to returning the value.
        """
        return self._module_name

    @module_name.setter
    def module_name(self, value: str) -> None:
        """
        Setter for the module_name attribute.

        Args:
            value (str): The updated string value for the module name.

        Uses controlled assignment to facilitate potential validation steps
        (e.g., checking for non-empty strings or ensuring a maximum length).
        Encapsulation can help enforce consistent and valid data.
        """
        # Example validation (commented out for illustration):
        # if not value:
        #     raise ValueError("Module name cannot be empty.")
        self._module_name = value

    @property
    def description(self) -> str:
        """
        Getter for the description attribute.

        Returns:
            str: The current value of the _description attribute.

        Encapsulates access to the description, allowing for future enhancements
        such as localized representations or dynamically computed values.
        """
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """
        Setter for the description attribute.

        Args:
            value (str): The updated string value for the module description.

        Provides a controlled way to assign the module's description,
        enabling the possibility for checks regarding format, length,
        or prohibited content.
        """
        # Example validation (commented out for illustration):
        # if len(value) < 10:
        #     raise ValueError("Description should be at least 10 characters long.")
        self._description = value

    @property
    def learning_outcomes(self) -> str:
        """
        Getter for the learning_outcomes attribute.

        Returns:
            str: The current value of the _learning_outcomes attribute.

        Encapsulates access to the learning outcomes, which detail the specific
        knowledge or competencies that students will develop upon successful
        completion of the module.
        """
        return self._learning_outcomes

    @learning_outcomes.setter
    def learning_outcomes(self, value: str) -> None:
        """
        Setter for the learning_outcomes attribute.

        Args:
            value (str): The updated string value for the module's learning outcomes.

        Uses encapsulation to permit specialized logic when updating the learning
        outcomes, such as checking for clarity, format (bulleted list, paragraph,
        etc.), or alignment with accreditation standards.
        """
        # Example validation (commented out for illustration):
        # if not value:
        #     raise ValueError("Learning outcomes must be defined.")
        self._learning_outcomes = value

    def display_module_information(self) -> None:
        """
        Prints the stored module information to the console in a structured format.

        By centralizing this output functionality, the method serves as a convenient
        mechanism for developers and academic staff to retrieve critical details
        associated with the university module without direct exposure of private
        attributes.
        """
        print("=== University Module Information ===")
        print(f"Module Name: {self.module_name}")
        print(f"Description: {self.description}")
        print(f"Learning Outcomes: {self.learning_outcomes}")
        print("=====================================")
