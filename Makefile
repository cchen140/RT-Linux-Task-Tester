CC = gcc
CFLAGS = -Wall -lpthread

x:	x.o
	$(CC) -o $@ $^ $(CFLAGS)

x_mibench:	x_mibench.o
	$(CC) -o $@ $^ $(CFLAGS)

all: x x_mibench

clean:
	rm -rf *.o x x_mibench output*
