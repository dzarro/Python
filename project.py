import matplotlib.pyplot as plt
import numpy as np
import math

def plot():
	
# Insert data into numpy arrays

	nu=np.array([7,7.3,7.7,8,8.3,8.7,9,9.3,9.7,10])
	Fnu=np.array([-21.88,-21.55,-21.67,-21.86,-22.09,-22.38,-22.63,-22.96,-23.43,-23.79])
	
# Compute linear least squares fit of power law

	coeff=np.polyfit(nu[2:],Fnu[2:],1)
	index=coeff[0]
	power=index*nu+coeff[1]
	
# Plot data

	plt.clf()
	plt.scatter(nu,Fnu)
	plt.plot(nu,Fnu,color='red',label='Measured Flux')
	plt.plot(nu,power,color='blue',label='Fitted Power Law')
	plt.ylabel('log'+r'$_{10}\ F_\nu$'+' (W m-2 Hz-1)')
	plt.xlabel('log'+r'$_{10}\ \nu$'+' (Hz)')
	plt.legend()
	plt.show(block=False)

	print(f"\nCygnus radio spectral index = {index:.2f}")
	
# Compute area using trapezoidal rule on frequency vs monoschromatic flux
# This yields total flux in watts per meter squared

	area=np.trapz(10**Fnu,10**nu)
	print(f"Cygnus flux = {area:.2e} Watts m-2")
	
# Compute luminosity from flux x 4 pi x distance squared
# Must convert parsecs to meters

	meters_per_parsec = 3.087*10**16  
	cygnus_parsecs=232.*10**6
	distance=cygnus_parsecs*meters_per_parsec
	print(f"Cygnus distance = {distance:.2e} meters")
	luminosity=area*4*math.pi*distance**2
	ergs=luminosity*10**7
	print(f"Cygnus radio luminosity = {luminosity:.2e} Watts")
		
if __name__ == "__main__":
    plot()	