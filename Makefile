main:
	python3 src/main.py samples/plain.c

character_count:
	python3 character_count.py words.txt

lint:
	black ./
	pylint **/*.py

clean:
	rm -f *.o logs/*
