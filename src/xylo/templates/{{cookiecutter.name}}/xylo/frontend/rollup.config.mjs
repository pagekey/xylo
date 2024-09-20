import typescript from '@rollup/plugin-typescript';

export default {
    input: 'src/index.tsx',
    output: {
        dir: 'dist',
        format: 'cjs',
        sourcemap: true,
        globals: {
          react: 'React',
        },
    },
    plugins: [typescript()],
    external: ['react', 'react-dom'],
};
