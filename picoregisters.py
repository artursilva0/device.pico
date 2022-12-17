from micropython import const

from microharp.types import HarpTypes
from microharp.register import HarpRegister, ReadWriteReg
from picofunction import HarpPwm


class HarpDigitalInputArrayRegister(ReadWriteReg):
    '''
    Abstract class for registers that listens to an array
    of digital input pins. Instantiates a picofunction.HarpDigitalInputArray
    '''
    def __init__(self, harpDigitalInputArray):
        super().__init__(HarpTypes.U8, 0)
        self.harp_digital_input_array = harpDigitalInputArray

    def __len__(self):
        return 1

    def read(self, typ):
        super().read(typ)
        return (self.harp_digital_input_array.state,)


class HarpDigitalOutputArrayRegister(ReadWriteReg):
    '''
    Abstract class for registers that control an array
    of digital output pins. Instantiates a picofunction.HarpDigitalOutputArray
    '''
    def __init__(self, harpDigitalOutputArray):
        super().__init__(HarpTypes.U8, 0)
        self.HarpDigitalOutputArray = harpDigitalOutputArray
        self.HarpDigitalOutputArray.clear_state()

    def __len__(self):
        return 1


class Set_HarpDigitalOutputArrayRegister(HarpDigitalOutputArrayRegister):
    '''
    Class used to "Set" (ON) any number of pins instantiated in a
    HarpDigitalOutputArrayRegister class object
    '''
    def __init__(self, harpDigitalOutputArray):
        super().__init__(harpDigitalOutputArray)

    def write(self, typ, mask):
        super().write(typ, mask)
        self.HarpDigitalOutputArray.set_state(mask[0])


class Clear_HarpDigitalOutputArrayRegister(HarpDigitalOutputArrayRegister):
    '''
    Class used to "Clear" (OFF) any number of pins instantiated in a
    HarpDigitalOutputArrayRegister class object
    '''
    def __init__(self, harpDigitalOutputArray):
        super().__init__(harpDigitalOutputArray)

    def write(self, typ, mask):
        super().write(typ, mask)
        self.HarpDigitalOutputArray.clear_state(mask[0])


class Toggle_HarpDigitalOutputArrayRegister(HarpDigitalOutputArrayRegister):
    '''
    Class used to "Toggle" (!State) any number of pins instantiated in a
    HarpDigitalOutputArrayRegister class object
    '''
    def __init__(self, harpDigitalOutputArray):
        super().__init__(harpDigitalOutputArray)

    def write(self, typ, mask):
        super().write(typ, mask)
        self.HarpDigitalOutputArray.toggle_state(mask[0])


class AdcRegister(HarpRegister):
    """Analog-to-digital converversion register.
    Maps a Pico ADC pin to a harp register."""

    def __init__(self, adcobject):
        super().__init__(HarpTypes.U16)
        self.adc = adcobject

    def __len__(self):
        return 1

    def read(self, typ):
        super().read(typ)
        return (self.adc.read_u16(),)


class AnalogStreamStateRegister(ReadWriteReg):
    """Enables/disables the AdcRegister stream."""
    def __init__(self, picoObject):
        super().__init__(HarpTypes.U8, 0)
        self.picoObject = picoObject

    def write(self, typ, value):
        super().write(typ, value)
        if (value[0] > 0):
            self.picoObject.adc_event.enable()
        else:
            self.picoObject.adc_event.disable()


class PwmFreqRegister(ReadWriteReg):
    """
    Stores and modified the PWM Frequency generated by Pico.
    Updates the frequency property of an harpPwm object.
    """
    def __init__(self, harpPWM):
        super().__init__(HarpTypes.U16, HarpPwm.MinFrequency)
        self.harpPWM = harpPWM

    def __len__(self):
        return 1

    def validate(self, value):
        if (value[0] < HarpPwm.MinFrequency):
            raise ValueError('Invalid input value.')
        return value

    def write(self, typ, value):
        super().write(typ, self.validate(value))
        self.harpPWM.frequency = value[0]


class PwmDutycycleRegister(ReadWriteReg):
    """
    Stores and modified the PWM Duty cycle generated by Pico.
    Updates the dutycyle property of an harpPwm object.
    """
    def __init__(self, harpPWM):
        super().__init__(HarpTypes.U8, HarpPwm.MinDutyCycle)
        self.harpPWM = harpPWM
        self.write(self.typ, (0,))  # Default to 0 % duty cycle

    def __len__(self):
        return 1

    def validate(self, value):
        if ((value[0] > 100) or (value[0] < HarpPwm.MinDutyCycle)):
            raise ValueError('Invalid input value.')
        return value

    def write(self, typ, value):
        super().write(typ, self.validate(value))
        self.harpPWM.dutycyle = value[0]


class PwmStartRegister(ReadWriteReg):
    """
    Starts a Pico PWM output signal.
    Calls "start()" from an HarpPwm object.
    """
    def __init__(self, harpPWM):
        super().__init__(HarpTypes.U8, 0)
        self.harpPWM = harpPWM

    def __len__(self):
        return 1

    def write(self, typ, value):
        if (self.harpPWM.enabled is False):
            # Start a new PWM with the set values
            super().write(typ, value)
            self.harpPWM.start()
        else:
            # Restart an already running PWM with new values
            super().write(typ, value)
            self.harpPWM.start()


class PwmStopRegister(ReadWriteReg):
    """
    Stops a Pico PWM output signal.
    Calls "stop()" from an HarpPwm object.
    """
    def __init__(self, harpPWM):
        super().__init__(HarpTypes.U8, 0)
        self.harpPWM = harpPWM

    def __len__(self):
        return 1

    def write(self, typ, value):
        if (self.harpPWM.enabled is True):
            super().write(typ, value)
            self.harpPWM.stop()
        else:
            super().write(typ, value)

