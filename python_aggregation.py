class A:
    def method_a(self):
        print("Method A from class A")


# Define class B
class B:
    A_instance = A()

    def __init__(self):
        self.instance_of_A = A()  # Creating an instance of class A inside class B

    def method_b(self):
        print("Method B from class B")
        self.instance_of_A.method_a()  # Accessing method_a from class A


# Define main function to execute the script
def main():
    # Creating an instance of class B
    object_of_B = B()
    # Calling method_b which will in turn call method_a from class A
    object_of_B.method_b()
    object_of_B.instance_of_A.method_a()


# If the script is executed directly, call the main function


if __name__ == "__main__":
    main()
