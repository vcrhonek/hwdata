
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

int errors = 0;

int linterr(char *reason, char *line, int number) {
	printf("Error on pcitable line %d: %s\n%s",
	       number, reason, line);
	errors++;
}

int main() {
	int fd;
	int vend, dev, subvend, subdev;
	char module[128], desc2[256], line[512];
	FILE *foo;
	int linenum = 0, ret;
	struct stat sbuf;

	foo = fopen("pcitable","r");
	while (fgets(line,512, foo)) {
		linenum++;
		if (line[0] == '#' || isspace(line[0]))
			continue;
		if (line[6] != '\t' || line[13] != '\t')  {
			linterr("bad format", line, linenum);
			continue;
		}
		if ((ret = sscanf(line,"%x\t%x\t\"%[^\"]\"",
			    &vend,&dev,&module)) != 3) {
			ret = sscanf(line,"%x\t%x\t%x\t%x\t\"%[^\"]\"",
			    &vend,&dev,&subvend,&subdev,&module);
			if (ret != 5) {
				linterr("bad format",line,linenum);
				continue;
			}
		}
		if (vend > 0xffff || vend < 1) {
			linterr("bad vendor id",line,linenum);
			continue;
		}
		if (dev > 0xffff || dev < 0) {
			linterr("bad device id",line,linenum);
			continue;
		}
		if (ret == 6)  {
			if (line[20] != '\t' || line[27] != '\t') {
				linterr("bad format", line, linenum);
				continue;
			}
			if (subvend > 0xffff || subvend < 1) {
				linterr("bad subvendor id",line,linenum); 
				continue;
			}
			if (subdev > 0xffff || subdev < 0) {
				linterr("bad subdevice id",line,linenum);
				continue;
			}
		}
	}
	return errors;
}
