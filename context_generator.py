import tenseal as ts
import tkinter as tk
from tkinter import filedialog
def save_file(title):
    root = tk.Tk()
    root.withdraw()  # Hide the root Tkinter window


    path = filedialog.asksaveasfilename(
        title=title,
        confirmoverwrite= True,
        filetypes=[("TenSEAL files","*.tenseal")],
        defaultextension= ".tenseal"
    )

    if path:
        print(f"Selected file/folder: {path}")
        return path
    else:
        print("No file selected.")
        return None

context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]

        )
context.global_scale = 2 ** 40
context.generate_galois_keys()


pvt_context = context.serialize(save_secret_key=True, save_galois_keys=True, save_relin_keys=True, save_public_key=True) # Private / Secret Key Context

context.make_context_public() # Public Key Context


PVT_file = open(save_file("Save secret key"), "wb") # Saving Private Key Context
PVT_file.write(pvt_context)
PVT_file.close()

file = open(save_file("Save public key"), "wb") # Saving Public Key Context
file.write(context.serialize())
file.close()



