from string import Template

vinfo = {
    "var1": "value1",
    "var2": "value2"
}

class StringVars:
    def __init__(self):
        for key in vinfo.keys():
            setattr(self, key, vinfo[key])
    
SV = StringVars()


string2format = Template("This is $var1")

print string2format.substitute(vars(SV))
