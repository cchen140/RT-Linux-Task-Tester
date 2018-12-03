CC = gcc
CFLAGS = -Wall -lpthread

x:	x.o
	$(CC) -o $@ $^ $(CFLAGS)

mix:	mix.o
	$(CC) -o $@ $^ $(CFLAGS)

all: x mix

clean:
	rm -rf *.o x mix output*
