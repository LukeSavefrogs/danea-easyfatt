/**
 * This script takes a markdown title and converts it to a slug.
 */
import process from 'node:process';
import GithubSlugger from 'github-slugger';

const title = process.argv[2].replace(/^#*\s*/, "", "g");
const slugger = new GithubSlugger();

console.log(slugger.slug(title));
