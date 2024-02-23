
/**
 * Compiles two shaders, links them together, looks up their uniform locations,
 * and returns the result. Reports any shader errors to the console.
 *
 * @param {string} vs_source - the source code of the vertex shader
 * @param {string} fs_source - the source code of the fragment shader
 * @return {WebGLProgram} the compiled and linked program
 */
function compile(vs_source, fs_source) {
    const vs = gl.createShader(gl.VERTEX_SHADER)
    gl.shaderSource(vs, vs_source)
    gl.compileShader(vs)
    if (!gl.getShaderParameter(vs, gl.COMPILE_STATUS)) {
        console.error(gl.getShaderInfoLog(vs))
        throw Error("Vertex shader compilation failed")
    }

    const fs = gl.createShader(gl.FRAGMENT_SHADER)
    gl.shaderSource(fs, fs_source)
    gl.compileShader(fs)
    if (!gl.getShaderParameter(fs, gl.COMPILE_STATUS)) {
        console.error(gl.getShaderInfoLog(fs))
        throw Error("Fragment shader compilation failed")
    }

    const program = gl.createProgram()
    gl.attachShader(program, vs)
    gl.attachShader(program, fs)
    gl.linkProgram(program)
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.error(gl.getProgramInfoLog(program))
        throw Error("Linking failed")
    }
    
    const uniforms = {}
    for(let i=0; i<gl.getProgramParameter(program, gl.ACTIVE_UNIFORMS); i+=1) {
        let info = gl.getActiveUniform(program, i)
        uniforms[info.name] = gl.getUniformLocation(program, info.name)
    }
    program.uniforms = uniforms

    return program
}

/**
 * Runs the animation using requestAnimationFrame. This is like a loop that
 * runs once per screen refresh, but a loop won't work because we need to let
 * the browser do other things between ticks. Instead, we have a function that
 * requests itself be queued to be run again as its last step.
 * 
 * @param {Number} milliseconds - milliseconds since web page loaded; 
 *        automatically provided by the browser when invoked with
 *        requestAnimationFrame
 */
function tick(milliseconds) {
    const seconds = milliseconds / 1000
    draw(seconds)
    requestAnimationFrame(tick) // <- only call this here, nowhere else
}

/**
 * Sends per-vertex data to the GPU and connects it to a VS input
 * 
 * @param data    a 2D array of per-vertex data (e.g. [[x,y,z,w],[x,y,z,w],...])
 * @param loc     the layout location of the vertex shader's `in` attribute
 * @param mode    (optional) gl.STATIC_DRAW, gl.DYNAMIC_DRAW, etc
 * 
 * @returns the ID of the buffer in GPU memory; useful for changing data later
 */
function supplyDataBuffer(data, loc, mode) {
    if (mode === undefined) mode = gl.STATIC_DRAW
    
    const buf = gl.createBuffer()
    gl.bindBuffer(gl.ARRAY_BUFFER, buf)
    const f32 = new Float32Array(data.flat())
    gl.bufferData(gl.ARRAY_BUFFER, f32, mode)
    gl.vertexAttribPointer(loc, data[0].length, gl.FLOAT, false, 0, 0)
    gl.enableVertexAttribArray(loc)
    
    return buf;
}
const IdentityMatrix = new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1])

function setupGeometry(geom) {
    var triangleArray = gl.createVertexArray()
    gl.bindVertexArray(triangleArray)
    for(let i=0; i<geom.attributes.length; i+=1) {
        let data = geom.attributes[i]
        supplyDataBuffer(data, i)
    }

    var indices = new Uint16Array(geom.triangles.flat())
    var indexBuffer = gl.createBuffer()
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indexBuffer)
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW)

    return {
        mode: gl.TRIANGLES,
        count: indices.length,
        type: gl.UNSIGNED_SHORT,
        vao: triangleArray
    }
}
const EarthTone = new Float32Array([0.8, 0.6, 0.4, 1])
/**
 * Clears the screen, sends two uniforms to the GPU, and asks the GPU to draw
 * several points. Note that no geometry is provided; the point locations are
 * computed based on the uniforms in the vertex shader.
 *
 * @param {Number} seconds - the number of seconds since the animation began
 */
function draw(seconds) {
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT) 
    gl.useProgram(program)
    
    gl.bindVertexArray(terrain.vao)

    // View
    let eye = [1,1,1]
    let v = m4view(eye, [0, 0, 0], [0, 0, 1])
    let m = m4mul(m4rotZ(seconds /2), m4rotZ(-Math.PI/2))

    let ld = normalize([2,2,2])

    gl.uniform3fv(program.uniforms.lightdir, ld)
    gl.uniform3fv(program.uniforms.lightcolor, [1,1,1])
    gl.uniform3fv(program.uniforms.eye, [0,0,1])
    gl.uniform4fv(program.uniforms.color, EarthTone)

    // Perspective
    gl.uniformMatrix4fv(program.uniforms.p, false, p)
    gl.uniformMatrix4fv(program.uniforms.mv, false, m4mul(v,m))

    gl.drawElements(terrain.mode, terrain.count, terrain.type, 0)
    
}

/** Resizes the canvas to completely fill the screen */
function fillScreen() {
    let canvas = document.querySelector('canvas')
    document.body.style.margin = '0'
    canvas.style.width = '100vw'
    canvas.style.height = '100vh'
    canvas.width = canvas.clientWidth
    canvas.height = canvas.clientHeight
    canvas.style.width = ''
    canvas.style.height = ''
    if (window.gl) {
        gl.viewport(0,0, canvas.width, canvas.height)
        window.p = m4perspNegZ(0.1, 10, 1.5, canvas.width, canvas.height)
    }
}

function createTerrain(gridsize, faults, weather) {
    terrain = {
        "attributes": 
        [
            [
                
            ]
        ],
        "triangles":
        [

        ]
        
    }
    for (let i = 0; i < gridsize * (gridsize - 1) - 1; i+= 1) {
        // Triangles
        if ((i+1) % gridsize != 0) {
            terrain.triangles.push([i, i+1, i+gridsize])
            terrain.triangles.push([i+1, i+gridsize, i+gridsize+1])
        }
    }
    mx = gridsize - 1
    for (let row = 0; row < gridsize; row += 1) {
        for (let col = 0; col < gridsize; col += 1) {
            terrain.attributes[0].push([2 * row / mx - 1, 2 * col / mx - 1, 0 ])
        }
    }
    let len = terrain.attributes[0].length
    for (let f = 0; f < faults; f += 1) {
        let x = Math.random() * 2 - 1
        let y = Math.random() * 2 - 1
        let rand_p = new Float32Array([x, y, 0])
        let theta = Math.random() * Math.PI * 2
        let normal = new Float32Array([Math.cos(theta), Math.sin(theta), 0])
        
        for (let p = 0; p < len; p+=1) {
            let point = terrain.attributes[0][p]
            let b = new Float32Array([point[0], point[1], point[2]])
            if (dot(sub(b, rand_p), normal) > 0) {
                terrain.attributes[0][p][2] += 0.1
            } else {
                terrain.attributes[0][p][2] -= 0.1
            }
        }
    }

    // Get max and min height
    let minh = Infinity
    let maxh = -Infinity
    
    for (let v = 0; v < len; v += 1) {
        let h = terrain.attributes[0][v][2]
        if (h < minh) {
            minh = h
        }
        if (h > maxh) {
            maxh = h
        }
    }

    // Normalize heights
    for (let v = 0; v < len; v += 1) {
        terrain.attributes[0][v][2] = (terrain.attributes[0][v][2] - ((maxh + minh) / 2)) / (maxh - minh)
    }
    let g = terrain.attributes[0]
    for (let w = 0; w < weather; w += 1) {
        for (let w_v = 0; w_v < len; w_v += 1) {
            let w_side = Math.sqrt(len)
            let sides = 0
            let tot = 0
            if (w_v < w_side) {
                tot += g[w_v + w_side][2]
                sides += 1
            } else if (w_v >= len - w_side) {
                tot += g[w_v - w_side][2]
                sides += 1
            } else {
                tot += g[w_v - w_side][2]
                tot += g[w_v + w_side][2]
                sides += 2
            }

            // Calculate e and w
            if (w_v % w_side == 0) {
                tot += g[w_v+1][2]
                sides += 1
            } else if ((w_v + 1) % w_side == 0) {
                tot += g[w_v-1][2]
                sides += 1
            } else {
                tot += g[w_v-1][2]
                tot += g[w_v+1][2]
                sides += 2
            }
            let m = tot / sides

            g[w_v][2] = (g[w_v][2] + m) / 2
        }
    }

    return terrain
}

// Add normals
function addNormals(geom) {
    let ni = geom.attributes.length
    geom.attributes.push([])
    let total = geom.attributes[0].length
    let side = Math.sqrt(total)
    let g = geom.attributes[0]
    for(let i = 0; i < total; i+=1) {
            let n = []
            let s = []
            let e = []
            let w = []

            // Calculate n and s
            if (i < side) {
                n = g[i]
                s = g[i + side]
                
            } else if (i >= total - side) {
                n = g[i - side]
                s = g[i]
            } else {
                n = g[i - side]
                s = g[i + side]
            }

            // Calculate e and w
            if (i % side == 0) {
                w = g[i]
                e = g[i+1]
            } else if ((i + 1) % side == 0) {
                w = g[i-1]
                e = g[i]
            } else {
                w = g[i-1]
                e = g[i+1]
            }
            let e1 = sub(n, s)
            let e2 = sub(w, e)
            let norm = cross(e1,e2)
            geom.attributes[ni].push(norm)
        }
    for(let i = 0; i < geom.attributes[0].length; i+=1) {
        geom.attributes[ni][i] = normalize(geom.attributes[ni][i])
    }
    console.log(geom.attributes[ni])
    
}

/**
 * Fetches, reads, and compiles GLSL; sets two global variables; and begins
 * the animation
 */


flag = 0
async function setup() {
    window.gl = document.querySelector('canvas').getContext('webgl2',
        // optional configuration object: see https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/getContext
        {antialias: false, depth:true, preserveDrawingBuffer:true}
    )
    const vs = await fetch('vs.glsl').then(res => res.text())
    const fs = await fetch('fs.glsl').then(res => res.text())
    window.program = compile(vs,fs)
    gl.enable(gl.DEPTH_TEST)
    gl.enable(gl.BLEND)
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA)
    
    document.querySelector('#submit').addEventListener('click', event => {
        const gridsize = Number(document.querySelector('#gridsize').value) || 2
        const faults = Number(document.querySelector('#faults').value) || 0
        const weather = Number(document.querySelector('#weather').value) || 0
        // TO DO: generate a new gridsize-by-gridsize grid here, then apply faults to it   
        const terrain = createTerrain(gridsize, faults, weather)
        addNormals(terrain)
        window.terrain = setupGeometry(terrain)
        fillScreen()
        window.addEventListener('resize', fillScreen)
        if (flag == 0) {
            requestAnimationFrame(tick) // <- ensure this function is called only once, at the end of setup
            flag = 1
        }
        
    })
    
}

window.addEventListener('load', setup)
