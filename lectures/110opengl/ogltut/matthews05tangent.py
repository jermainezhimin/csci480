# -*- coding: utf-8 -*-
import os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import compileShader, compileProgram
import pygame           
from pygame.locals import *
import numpy as N
from ctypes import c_void_p

from transforms import *
from controls import *
from texture import loadTexture
from shaders import loadProgram
from psurfacetangent import *

def main ():
    # pygame initialization
    pygame.init()
    screen = pygame.display.set_mode((640,480), OPENGL|DOUBLEBUF)
    clock = pygame.time.Clock()

    # OpenGL initializations
    glClearColor(0.0,0.0,0.4,0.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    # cull triangles facing away from camera
    #glEnable(GL_CULL_FACE)
 
    # make vertex array
    VertexArrayID = glGenVertexArrays(1)
    glBindVertexArray(VertexArrayID)
   
    # compile shaders
    programID = loadProgram(
        os.path.join("shaders","shader05tangent.vert"),
        os.path.join("shaders","shader05tangent.frag")
        )
    print "programID:", programID
    # get handle for "MVP" uniform
    ViewMatrixID = glGetUniformLocation(programID, "V")
    ModelMatrixID = glGetUniformLocation(programID, "M")
    ProjectionMatrixID = glGetUniformLocation(programID, "P")
    print "P,V,M:",ProjectionMatrixID,ViewMatrixID,ModelMatrixID

    # vertex, normal, and texture uv data:
    vertNormUVData, vertNormUVIndices = sphere(1,32,64)
    # 4 point coords, 4 norm coords, 2 uvs:
    numberOfVertices = len(vertNormUVIndices)
    print "N Triangles:", numberOfVertices/3
    
    # vertex buffer for points, norms, uvs
    vertNormUVBuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertNormUVBuffer)
    glBufferData(GL_ARRAY_BUFFER, vertNormUVData, GL_STATIC_DRAW)
    # vertex buffer for indices
    vertNormUVIndexBuffer = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, vertNormUVIndexBuffer)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, vertNormUVIndices, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    # get handle for light position
    glUseProgram(programID)
    LightID = glGetUniformLocation(programID, "lightDirection")
    whichRibsID = glGetUniformLocation(programID, "whichRibs")
    print "LightID, whichRibs:", LightID, whichRibsID

    # get attribute locations
    PositionID = glGetAttribLocation(programID, "positionBuffer")
    NormalID = glGetAttribLocation(programID, "normalBuffer")
    uvID = glGetAttribLocation(programID, "uvBuffer")
    print "pos, norm, uv:", PositionID, NormalID, uvID

    # control object
    eye = vec((0,2,3))
    focus = vec((0,0,0))
    control = Control(pos=eye,
                      fwd=focus-eye)
    
    lightDirection = normalize(vec((5,3,1,0)))
    whichRibs = 0
    time = 0.0
    running = True
    while running:
        clock.tick(30)
        time += 0.0333;
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_SPACE:
                    whichRibs = (whichRibs + 1) % 2
            if event.type == pygame.MOUSEBUTTONDOWN:
                control.handleMouseButton(event.button)
        control.handleMouseMotion()
        control.handleKeyboard()

        # compute MVP
        ProjectionMatrix = control.getProjectionMatrix()
        ViewMatrix = control.getViewMatrix()
        ModelMatrix = control.getModelMatrix()
        if False: # identity transform for testing
            ident = N.identity(4,dtype=N.float32)
            ProjectionMatrix = ident
            ViewMatrix = ident
            ModelMatrix = ident

        # draw into opengl context
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # use our shader
        glUseProgram(programID)
        # send our transform to the shader
        glUniformMatrix4fv(ProjectionMatrixID, 1, GL_TRUE, ProjectionMatrix)
        glUniformMatrix4fv(ModelMatrixID, 1, GL_TRUE, ModelMatrix)
        glUniformMatrix4fv(ViewMatrixID, 1, GL_TRUE, ViewMatrix)
        # GL_TRUE: transpose the matrix for opengl column major order

        # uniforms
        ld = N.dot(rotationYMatrix(time), lightDirection);
        glUniform4fv(LightID, 1, ld)
        glUniform1i(whichRibsID, whichRibs)

        # only one attribute buffer:
        glBindBuffer(GL_ARRAY_BUFFER, vertNormUVBuffer)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, vertNormUVIndexBuffer)
        # three different attribute pointers:
        bytesPerFloat = 4
        bytesPerShort = 2
        # points:
        if PositionID >= 0:
            glEnableVertexAttribArray(PositionID)
            glVertexAttribPointer(
                PositionID,             # attrib  
                4,                      # size
                GL_FLOAT,               # type
                GL_FALSE,               # normalized?
                18*bytesPerFloat,       # stride
                c_void_p(0)             # array buffer offset
                )
        # normals:
        if NormalID >= 0:
            glEnableVertexAttribArray(NormalID)
            glVertexAttribPointer(
                NormalID,
                4,
                GL_FLOAT,
                GL_FALSE,
                18*bytesPerFloat,
                c_void_p(4*bytesPerFloat))
        # uvs:
        if uvID >= 0:
            glEnableVertexAttribArray(uvID)
            glVertexAttribPointer(
                uvID,
                2,
                GL_FLOAT,
                GL_FALSE,
                18*bytesPerFloat,
                c_void_p(16*bytesPerFloat))
        
        # draw the triangle
        glDrawElements(GL_TRIANGLES, numberOfVertices*bytesPerShort,
                       GL_UNSIGNED_SHORT, c_void_p(0))

        if PositionID >= 0:
            glDisableVertexAttribArray(PositionID)
        if NormalID >= 0:
            glDisableVertexAttribArray(NormalID)
        if uvID >= 0:
            glDisableVertexAttribArray(uvID)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        # swap buffers
        pygame.display.flip()
        
    glDeleteProgram(programID)

if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
