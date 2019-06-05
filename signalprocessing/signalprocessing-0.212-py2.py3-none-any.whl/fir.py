class fir:
    def __init__(self):
        self.x=0
    def lpf(self,N,wc,win):
        import math
        import matplotlib.pyplot as plt
        if(win=='hamm'):
            alp=(N-1)/2;
            pi=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=0.54-0.46*math.cos((2*pi*n)/(N-1));
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=wc/pi;
                else:
                    hd[n]=math.sin(wc*(n-alp))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using hamming window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using hamming window ')
            plt.show();
        elif(win=='hann'): 
            alp=(N-1)/2;
            pi=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=0.5-0.5*math.cos((2*pi*n)/(N-1));
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=wc/pi;
                else:
                    hd[n]=math.sin(wc*(n-alp))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using hanning window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using hanning window ')
            plt.show();
        elif(win=='rect'): 
            alp=(N-1)/2;
            pi=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=1;
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=wc/pi;
                else:
                    hd[n]=math.sin(wc*(n-alp))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using rectangular window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using rectangular window ')
            plt.show();
        else: 
            alp=(N-1)/2;
            pi=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=1;
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=wc/pi;
                else:
                    hd[n]=math.sin(wc*(n-alp))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using rectangular window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using rectangular window ')
            plt.show();
    def hpf(self,N,wc,win):
        import math
        import matplotlib.pyplot as plt
        if(win=='hamm'):
            alp=(N-1)/2;
            pi=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=0.54-0.46*math.cos((2*pi*n)/(N-1));
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=(pi-wc)/pi;
                else:
                    hd[n]= -math.sin(wc*(n-alp))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using hamming window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using hamming window ')
            plt.show();
        elif(win=='hann'): 
            alp=(N-1)/2;
            pi=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=0.5-0.5*math.cos((2*pi*n)/(N-1));
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=(pi-wc)/pi;
                else:
                    hd[n]= -math.sin(wc*(n-alp))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using hanning window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using hanning window ')
            plt.show();
        elif(win=='rect'): 
            alp=(N-1)/2;
            pi=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=1;
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=(pi-wc)/pi;
                else:
                    hd[n]= -math.sin(wc*(n-alp))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using rectangular window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using rectangular window ')
            plt.show();
        else: 
            alp=(N-1)/2;
            pi=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=1;
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=(pi-wc)/pi;
                else:
                    hd[n]= -math.sin(wc*(n-alp))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using rectangular window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using rectangular window ')
            plt.show();
            
    def bpf(self,N,wc1,wc2,win):
        import math
        import matplotlib.pyplot as plt
        if(win=='hamm'):
            alp=(N-1)/2;
            pi=math.pi;
            sin=math.sin;
            w=[0]*N;
            for n in range(N):
                w[n]=0.54-0.46*math.cos((2*pi*n)/(N-1));
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=(wc2-wc1)/pi;
                else:
                    hd[n]=(sin(wc2*(n-alp))-sin(wc1*(n-alp)))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using hamming window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using hamming window ')
            plt.show();
        elif(win=='hann'): 
            alp=(N-1)/2;
            pi=math.pi;
            sin=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=0.5-0.5*math.cos((2*pi*n)/(N-1));
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=(wc2-wc1)/pi;
                else:
                    hd[n]=(sin(wc2*(n-alp))-sin(wc1*(n-alp)))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using hanning window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using hanning window ')
            plt.show();
        elif(win=='rect'): 
            alp=(N-1)/2;
            pi=math.pi;
            sin=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=1;
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=(wc2-wc1)/pi;
                else:
                    hd[n]=(sin(wc2*(n-alp))-sin(wc1*(n-alp)))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using rectangular window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using rectangular window ')
            plt.show();
        else: 
            alp=(N-1)/2;
            pi=math.pi;
            sin=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=1;
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=(wc2-wc1)/pi;
                else:
                    hd[n]=(sin(wc2*(n-alp))-sin(wc1*(n-alp)))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using rectangular window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using rectangular window ')
            plt.show();
            
    def bsf(self,N,wc1,wc2,win):
        import math
        import matplotlib.pyplot as plt
        if(win=='hamm'):
            alp=(N-1)/2;
            pi=math.pi;
            sin=math.sin;
            w=[0]*N;
            for n in range(N):
                w[n]=0.54-0.46*math.cos((2*pi*n)/(N-1));
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=(pi-(wc2-wc1))/pi;
                else:
                    hd[n]=-(sin(wc2*(n-alp))-sin(wc1*(n-alp)))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using hamming window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using hamming window ')
            plt.show();
        elif(win=='hann'): 
            alp=(N-1)/2;
            pi=math.pi;
            sin=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=0.5-0.5*math.cos((2*pi*n)/(N-1));
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=(pi-(wc2-wc1))/pi;
                else:
                    hd[n]=-(sin(wc2*(n-alp))-sin(wc1*(n-alp)))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using hanning window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using hanning window ')
            plt.show();
        elif(win=='rect'): 
            alp=(N-1)/2;
            pi=math.pi;
            sin=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=1;
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=(pi-(wc2-wc1))/pi;
                else:
                    hd[n]=-(sin(wc2*(n-alp))-sin(wc1*(n-alp)))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using rectangular window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using rectangular window ')
            plt.show();
        else: 
            alp=(N-1)/2;
            pi=math.pi;
            sin=math.pi;
            w=[0]*N;
            for n in range(N):
                w[n]=1;
            hd=[0]*N;
            h=[0]*N;
            for n in range(N):
                if n==alp:
                    hd[n]=(pi-(wc2-wc1))/pi;
                else:
                    hd[n]=-(sin(wc2*(n-alp))-sin(wc1*(n-alp)))/(pi*(n-alp));
            for n in range(N):
                 h[n]=hd[n]*w[n];
            plt.subplot(2,1,1);
            plt.stem(range(N),h);
            plt.title('Impulse response of FIR filter using rectangular window ')
            Hr=[0]*630;
            Hi=[0]*630;
            w2=-pi;
            for w1 in range(630):
                for n in range(N):
                    Hr[w1]=Hr[w1]+h[n]*math.cos(w2*n);
                    Hi[w1]=Hi[w1]-h[n]*math.sin(w2*n);
                w2=w2+0.01;
            Hm=[0]*630;
            for w1 in range(630):
                Hm[w1]=math.sqrt(Hr[w1]*Hr[w1]+ Hi[w1]*Hi[w1]);
            t=[0]*630
            st=-pi
            for i in range(630):
                t[i]=st;
                st+=0.01
            plt.subplot(2,1,2);
            plt.plot(t,Hm);
            plt.title('Frequency response of FIR filter using rectangular window ')
            plt.show();
            
            
            
            