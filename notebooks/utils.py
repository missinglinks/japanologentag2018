import matplotlib.pyplot as plt
from matplotlib_venn import venn3, venn2

def venn_diagram(a, b, c=None):
    """
    Draws a venn diagram of the user lists from two or three ChannelUserList objects
    """
    a_set = set([ x.id for x in a ])
    b_set = set([ x.id for x in b ])
    plt.figure(figsize=(15,15))
    if not c:
        venn2([ set(a_set), set(b_set)], set_labels=(a.label, b.label) )
    else:
        c_set = set([ x.id for x in c])
        venn3([ set(a_set), set(b_set), set(c_set)], 
              set_labels=(a.label, b.label, c.label) )        
    plt.show()