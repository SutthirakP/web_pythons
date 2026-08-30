students = [1,2,3,4]


students[3] = "CoC"

students.extend(["end1", "end2"])
# students.extend("end3")
# students.extend("end4")

students.insert(1, "New Value")
print(students)
# students.remove("New Value")
# print(students)
students.pop(1)
students.pop()
print(students)

if "CoC" in students:
    print("IN")
    
print(f" CoC is indexed at: {students.index('CoC')}")

print(students.count("CoC"))

mynumber = [1,2,3,4]

# mynumber.sort()
print(sorted(mynumber))
print(mynumber)