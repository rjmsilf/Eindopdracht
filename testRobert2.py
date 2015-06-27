from Symbolische_manipulatie import *

o=Constant(0)
a=Constant(1)
b=Constant(2)
c=Constant(3)
d=Constant(4)
e=CosNode(2)
x=Variable('x')
y=Variable('y')
z=Variable('z')

iets=(x**b)**c
#print(iets.simplify())
print(iets.derivative(x))
print(iets.hasvariable(x))

#NU VERANDERD

