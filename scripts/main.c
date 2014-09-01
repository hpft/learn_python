#include <Python.h>

int main(void){
	Py_Initialize();
	PyRun_SimpleString("Hello C");

	return 0;
}
