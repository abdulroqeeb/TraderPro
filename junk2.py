#grade converter
def gradeConverter():
    grade=float(raw_input('What is your grade? '))
    if grade < 60 :
                print 'Your grade is F'
    elif grade >= 60 and <= 69.99:
                print ' Your grade is D'
    elif grade >= 70 and <= 79.99:
                print ' Your grade is C'
    elif grade >= 80 and <= 89.99:
                print ' Your grade is B'
    elif grade >= 90:
                print ' Your grade is A'
    else End
print 'Problem [1] Complete'