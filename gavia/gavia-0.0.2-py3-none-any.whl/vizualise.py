import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 20})

def imgfootprint(pix1,pix2,pix3,pix4,fovh,fovv,w1,w2):
    fig, ax 	= plt.subplots(figsize=(9, 9), dpi=60, facecolor='w', edgecolor='k')
    ax.scatter([ pix1[0] ],[ pix1[1] ],s=100, c='r')
    ax.scatter([ pix2[0] ],[ pix2[1] ],s=100, c='b')
    ax.scatter([ pix3[0] ],[ pix3[1] ],s=100,  c='k')
    ax.scatter([ pix4[0] ],[ pix4[1] ],s=100,  c='g')
    ax.scatter([ 0 ],[ 0 ],s=100,  marker='x')
    ax.plot([ pix2[0],pix1[0],pix3[0],pix4[0],pix2[0] ],[pix2[1],pix1[1],pix3[1],pix4[1],pix2[1]],linewidth=1.5)
    ax.plot([-fovh/2.0, fovh/2.0], [0,0], c='orange', linewidth=1)
    ax.plot([0,0],[-fovv/2.0, fovv/2.0], c='orange', linewidth=1)

    # if roll is 0 
    ax.plot([-w1/2.0, w1/2.0], [pix1[1],pix2[1]], c='purple', linewidth=1)
    ax.plot([-w2/2.0, w2/2.0], [pix3[1],pix4[1]], c='purple', linewidth=1)


    ax.set_xlim((-2,2))
    ax.set_ylim((-2,2))
    plt.grid(True)
    plt.show()