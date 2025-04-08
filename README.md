# NUEVOLENS
### A project that combines facial recognition with homomorphic encryption to achieve secured surveillance

# Introduction
- Has two streams running in parallel; HE stream is stream 1, AES is stream 2
- Project is divided into 3 modules; edge node 1, server node 2, admin node 3
- Edge node accesses video feed of webcam
- module 1_1 Collects face data, encrypts with HE public_context.tenseal and sends to module 2.1
- module 1_2 encrypts frames through 256-bit AES and sends to module 2.2
- module 2.1 processes and sends encrypted data to module 3.1
- module 2.2 saves the incoming encrypted frames as 10 second encrypted videos in hourly folders
- module 3 decrypts the data, generates suitable logs and notifications
- module 3.2 can search and decrypt AES encrypted videos
- gui3_1 is GUI module that starts and stops module_3.1
- gui3_2 is GUI module that starts and stops module_3.2
- add_identity.py is used to generate encrypted embeddings pickle file to be used for comparison
- context_generator is used to generate public and private HE keys
- decrypt_he_emb is used to decrypt and plot encrypted embeddings stored at runtime


# Installation & Execution
1. Set interpreter of your environment to python 3.9. python 3.10 and later are incompatible with tenseal (our homomorphic encryption library)  
2. Install requirements
```sh
$ pip install -r requirements.txt
```
3. The code above is able to implement module 1 on Raspberry Pi 5 with 8GB RAM
4. For ARM architechture of Raspberry Pi, TenSEAL is unavailable, hence you will have to build it from scratch. For more info visit [pypi](https://pypi.org/project/tenseal/0.1.0a0/)
5. Create a virtual environment for linux based systems before installing dependencies for module 1
6. Set the IP addresses and file_path dependencies in respective python files
7. Face Recognition model InceptionResnet with VGGFACE2 is a 109 MB file stored at [torch folder in Drive](https://drive.google.com/drive/folders/1jlIk2Z7BkRWWmF8duRDkaWMWesLRGGkK?usp=sharing "Go to Google Drive"). Download the *torch* folder
8. It must contain *checkpoints* folder which must contain a *.pt* file of 109 MB
9. Save the *torch* folder to your user account's .cache folder for running add_identity.py and module_1_1.py
10. Edit the file path of python 3.9 interpreter in both gu3_1.py and gui3_2.py
11. The interpreter must be the same being used for the rest of project that was used to install dependencies else other interpreter will not recognize the dependencies imported and cause errors.
12. Run gui3_1
```sh
$ python gui3_1.py
```
11. Then run module_2.1 and module_2.2
```sh
$ python module_2.1.py
$ python module_2.2.py
```
12. Then run nuevolens1.py, it will call 1.1 and 1.2 itself
```sh
$ python nuevolens1.py
```
13. For decrypting stored AES encrypted files, run gui3_2
```sh
$ python gui3_2.py
```
14. It will automatically run module_3.2 through an interactive GUI where you will be prompted to select AES key for decryption and the files to decrypt
15. Those files will then be decrypted
16. Use add_identity.py to define a new encrypted dataset, just add the file path of dataset folder containing folders of identities with their names and the folders containing face images.
17. Then run add_identity.py
```sh
$ python add_identity.py
```
18. Use decrypt_he_emb.py to decrypt HE encrypted embeddings saved at runtime and to plot them, add file path of saved he embeddings from module 2 and then run it
```sh
$ python decrypt_he_emb.py
```
19. Run context_generator.py to generate public/private TenSEAL context pair
```sh
$ python context_generator.py
```

Made By : [FASH](mailto:fashnuevolens@gmail.com)<br>
**Secured Surveillance, Ooooh Yeah!**
