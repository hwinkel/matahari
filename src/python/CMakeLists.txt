if(NOT WIN32)
FIND_PACKAGE(PythonInterp)

macro(py_module MODULE DIRECTORY)
    # Copy the Python file to the Binary directory
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/${DIRECTORY}/${MODULE}.py
         DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/${DIRECTORY})

    # Compile .pyc and .pyo files
    execute_process(COMMAND ${PYTHON_EXECUTABLE} -m py_compile ${MODULE}.py
                    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${DIRECTORY})
    execute_process(COMMAND ${PYTHON_EXECUTABLE} -O -m py_compile ${MODULE}.py
                    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${DIRECTORY})

    install(FILES ${CMAKE_CURRENT_BINARY_DIR}/${DIRECTORY}/${MODULE}.py
                  ${CMAKE_CURRENT_BINARY_DIR}/${DIRECTORY}/${MODULE}.pyc
                  ${CMAKE_CURRENT_BINARY_DIR}/${DIRECTORY}/${MODULE}.pyo
            DESTINATION ${PYTHON_SITE_PACKAGES}/${DIRECTORY})
endmacro(py_module)

if(WITH-QMF)
    execute_process(COMMAND ${PYTHON_EXECUTABLE} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"
                    OUTPUT_VARIABLE PYTHON_SITE_PACKAGES
                    OUTPUT_STRIP_TRAILING_WHITESPACE)

    py_module(__init__     matahari)
    py_module(rpc_server   matahari)
    py_module(core         matahari)
    py_module(api          matahari)
    py_module(__init__     matahari/shell)
    py_module(mode         matahari/shell)
    py_module(types        matahari/shell)
    py_module(__init__     matahari/shell/interpreter)
    py_module(interpreter  matahari/shell/interpreter)
    py_module(mode         matahari/shell/interpreter)
    py_module(command      matahari/shell/interpreter)

    install(PROGRAMS ${CMAKE_CURRENT_SOURCE_DIR}/mhsh
            DESTINATION bin)

endif(WITH-QMF)
endif(NOT WIN32)

