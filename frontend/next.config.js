/** @type {import('next').NextConfig} */
const nextConfig = {
  sassOptions: {
    includePaths: ['./src/styles']
  },
  output: 'export',
  distDir: 'out',
}

module.exports = nextConfig