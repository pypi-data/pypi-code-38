import numpy as np
from matplotlib import pyplot as plt

Mn=1.67e-27 #Mass of Neutrons (kg)
h=6.60e-34 #Planck's const (Js)

CF=(h*1e7)/Mn #(3.952) time should be in milisecond and wavelength should be in angstrom

class VENUS_chopper(object):

    def __init__(self, Pulse_frequency, pulse_width,delay ,SourceTOdetector , chopper_rotational_frequency, minimum_wavelength, distance_T3chopper_fr_source, distance_T1chopper_fr_source, distance_T2chopper_fr_source ):
        r"""

        Parameters
        ----------
        Pulse_frequency: float
            Pulse_frequency of neutron source in Hz

        pulse_width: float
            Neutrons emitted from the moderator with a certain wavelength
            :math:`\lambda` have a distribution of delayed emission times
            with :math:`FWHM(\lambda) \simeq pulsewidth \cdot \lambda`.
            Units are seconds/Angstroms.

        delay: float
            Additional time-of-flight to include in the calculations

        SourceTOdetector: float
            Distance travelled by the neutron to detector, in meters

        chopper_rotational_frequency: float
            rotational frequency of chopper, in Hz

        wavelength_center: float
            wavelength  center of the arriving neutron, in Angstrom
        """
        self.Pulse_frequency = Pulse_frequency
        self.pulse_width= float(pulse_width)
        self.delay = float(delay)
        self.SourceTOdetector= float(SourceTOdetector)
        self.chopper_rotational_frequency=chopper_rotational_frequency
        self.minimum_wavelength=minimum_wavelength
        self.distance_T3chopper_fr_source=distance_T3chopper_fr_source
        self.distance_T1chopper_fr_source=distance_T1chopper_fr_source
        self.distance_T2chopper_fr_source=distance_T2chopper_fr_source

    def Wavelength_width(self,distance, frequency):
        r"""
         neutron acceptable frame wavelength width for a particular frequency and distance travelled
        ----------
        distance: float
            distance travelled by neutrons, in meters
        frequency: float
            frequncy  in Hz

        Returns
        -------
        float
            wavelength (in Angstrom)
        """
        frequency = frequency / 1000
        time=(1/frequency)+ self.pulse_width

        return CF*(time/distance)



    def tof(self, distance, wavelength, pulsed=False):
        r"""
        Convert wavelength of arriving neutron to time of flight

        Parameters
        ----------
        wavelength: float
            wavelength of the arriving neutron, in Angstrom
        distance: float
            distance travelled by neutrons, in meters
        pulsed: bool
            Include the correction due to delayed emission of neutrons
            from the moderator

        Returns
        -------
        float
            time of flight (in milisecond)
        """

        loc = distance
        if pulsed is True:
            loc += CF * self.pulse_width
        return wavelength * loc / CF - self.delay



    # def time_delay_before_T3chopper_opens(self):
    #     r"""
    #       calculated the time when chopper T3 chopper opens
    #
    #       Returns
    #       -------
    #       float
    #           Opening time, in milisecond
    #     """
    #
    #     t03 =self.tof(self.distance_T3chopper_fr_source, self.minimum_wavelength)
    #     return(t03)

    def time_delay_before_chopper_opens(self, distance):
        r"""
          calculated the time when chopper T1 or T2  or T3 opens

          Parameters
          ----------
          distance: float
              distance travelled by neutrons to chopper, in meters

          Returns
          -------
          float
              Opening time, in milisecond
          """
        t0 =(distance*self.minimum_wavelength/CF) + (distance*self.pulse_width/self.distance_T3chopper_fr_source)
        return(t0)

    def openning_time_duration(self, distance, frequency):
        r"""
         calculated the acceptable open duration at any distance

         Parameters
         ----------
         distance: float
             distance travelled by neutrons to chopper, in meters

        frequency: float
            frequncy  in Hz

         Returns
         -------
         float
             Open duration , in milisecond
         """
        del_t=((distance/self.SourceTOdetector)*((1/frequency)-(2*self.pulse_width*(self.SourceTOdetector-self.distance_T3chopper_fr_source))/self.distance_T3chopper_fr_source))+self.pulse_width
        return(del_t*1000)


    def Chopper_phase_angle(self, distance): #Open Angle
        r"""
          calculated the phase angle

          Parameters
          ----------
          distance: float
              distance travelled by neutrons to chopper, in meters

          Returns
          -------
          float
              Opening window, in degrees
          """
        angular_velocity=self.chopper_rotational_frequency*2*np.pi
        radTodeg=360/(2*np.pi)
        return(self.openning_time_duration(distance, self.chopper_rotational_frequency)*angular_velocity*radTodeg)

    def making_plot(self, maximum_wavelength, total_pulse, ):

        r"""
                plot the time-distance diagram for different chopper configuration

                Parameters
                ----------
                maximum_wavelength: float
                    maximum wavelength of the arriving neutron, in Angstrom

                total_pulse: integer
                    total number of pulse

                Returns
                -------
                plot of the time-distance diagram
                """

        distance = np.arange(0, self.SourceTOdetector, 0.1)

        bandwidth = self.Wavelength_width(self.SourceTOdetector, self.Pulse_frequency)
        chpperwidth = self.Wavelength_width(self.SourceTOdetector, self.chopper_rotational_frequency)


        ch_wavelength = [self.minimum_wavelength, self.minimum_wavelength + chpperwidth]

        chopper_distance = np.array(
            [self.distance_T1chopper_fr_source, self.distance_T2chopper_fr_source, self.distance_T3chopper_fr_source])

        wavelengths2 = np.arange(self.minimum_wavelength, maximum_wavelength, bandwidth)

        npulse = total_pulse

        pulses = range(npulse)
        chopper_period = 1000. / self.chopper_rotational_frequency
        pulse_period = 1000. / self.Pulse_frequency

        plt.figure(figsize=(8, 5))

        [plt.plot(self.tof(distance, i) + 0 * pulse_period, distance, ':', label="%s $\AA$" % i) for i in wavelengths2]

        # lighthouse lines
        for pulse in pulses:
            [plt.plot(self.tof(distance, i) + pulse * chopper_period, distance, 'r') for i in ch_wavelength]

        # horizontal lines
        [
            [plt.hlines(i, self.time_delay_before_chopper_opens(i) + self.openning_time_duration(i,
                                                                                                 self.chopper_rotational_frequency) + (
                                    pulse - 1) * chopper_period,
                        self.time_delay_before_chopper_opens(i) + (pulse) * chopper_period,
                        colors='k', linestyles='solid')
             for i in chopper_distance]
            for pulse in range(npulse + 1)
        ]

        plt.xlabel('time in milisecond')
        plt.ylabel('distance in meters')
        plt.xlim(0, self.tof(self.SourceTOdetector, maximum_wavelength))
        plt.legend()
        plt.show()










