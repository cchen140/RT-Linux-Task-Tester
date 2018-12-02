CC = gcc
CFLAGS = -O3 -Wall -lpthread

x:	x.o
	$(CC) -o $@ $^ $(CFLAGS)
	strip $@

clean:
	rm -rf *.o x output*
