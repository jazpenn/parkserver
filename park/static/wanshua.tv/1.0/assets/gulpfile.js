'use strict';
 
var gulp = require('gulp');
var gutil = require('gulp-util');
var source = require('vinyl-source-stream');
var uglify = require('gulp-uglify');
var streamify = require('gulp-streamify');

// browserSync
var browserSync = require('browser-sync');

var watch_files = ['css/**', 'js/**', 'img/**', '../../../../templates/1.0/**'];

gulp.task('browser-sync', function() {
  browserSync({
    files: watch_files,
    reloadDebounce: 380,
    reloadDelay: 380,
    proxy: "localhost:8012"
  });
});

// gulp.task('browser-sync-local', function() {
//   browserSync({
//     files: watch_files,
//     reloadDebounce: 380,
//     reloadDelay: 380,
//     server: {
//       baseDir: "../../"
//     }
//   });
// });

// Sass
var sass = require('gulp-sass');

// Browserify
var browserify = require('browserify');
var watchify = require('watchify');

// Sass
gulp.task('sass', function () {
  gulp.src('sass/**/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('./css'));
});

gulp.task('sass:watch', function () {
  gulp.watch('sass/**/*.scss', ['sass']);
});

// Browserify
var b = browserify({
  entries: ['CommonJS/all.js'],
  cache: {},
  packageCache: {},
  plugin: [watchify]
});

gulp.task('browserify', bundle);

b.on('update', bundle);
b.on('log', gutil.log);

function bundle() {
  return b.bundle()
    .on('error', gutil.log.bind(gutil, 'Browserify Error'))
    .pipe(source('all.js'))
    .pipe(streamify(uglify()))
    .pipe(gulp.dest('./js'));
}

gulp.task('main', ['sass:watch', 'browserify', 'browser-sync']);
gulp.task('main-local', ['sass:watch', 'browserify', 'browser-sync-local']);
