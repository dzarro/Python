import matplotlib.pyplot as plt
import numpy as np
import math

def plot():
	
# Insert data into numpy arrays

	nu=np.array([7,7.3,7.7,8,8.3,8.7,9,9.3,9.7,10])
	Fnu=np.array([-21.88,-21.55,-21.67,-21.86,-22.09,-22.38,-22.63,-22.96,-23.43,-23.79])
	
# Plot data

	plt.plot(nu,Fnu)
	plt.ylabel("Log10 Fnu (W m-2 Hz-1)")
	plt.xlabel("Log10 Nu (Hz)")
	plt.show(block=False)
	
# Compute area using trapezoidal rule on frequency vs monoschromatic flux)
# This yields total flux in watts per meter squared

	area=np.trapz(10**Fnu,10**nu)
	print(f"\nCygnus flux = {area:.2e} Watts m-2")
	
# Compute luminosity from flux x 4 pi x distance squared
# Must convert parsecs to meters

	meters_per_parsec = 3.087*10**16  
	cygnus_parsecs=232.*10**6
	distance=cygnus_parsecs*meters_per_parsec
	print(f"Cygnus distance = {distance:.2e} meters")
	luminosity=area*4*math.pi*distance**2
	print(f"Cygnus luminosity = {luminosity:.2e} Watts ")
		
if __name__ == "__main__":
    plot()	