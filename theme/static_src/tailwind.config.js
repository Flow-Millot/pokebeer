module.exports = {
    content: [
        '../templates/**/*.html',
        '../../templates/**/*.html',
        '../../**/templates/**/*.html',
        "./node_modules/flowbite/**/*.js"
    ],
    plugins: [
        require('flowbite/plugin')
    ],
}