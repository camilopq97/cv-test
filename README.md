# Computer Vision results

The following code find the checkers at a Backgammon board.
# Use

* To run the solution, use the command:

        python main.py <input_path> <output_path>
        
    where `<input_path>` is the input folder (the sample `.jpg` figures and the `.info.json` should be there) and `<output_path>` is the output folder where you'll have the solution figures and the `.checjers.json` files for each image.

# Questions

1. How well do you expect this to work on other images?
    I hope it will work in almost all kind of images, especially where the contrast between the board and the checkers is enough. 
2. What are possible fail cases of this approach and how would you address them?
    A possible fail case is when the checkers are not perfectly aligned on the pipe. Also images like 'vertical4.jpg' where the initial perspective is too away of the ideal one. Also the checkers on the bar will be a problem, because sometimes the players put them close to the pipes.
    To solve this problems, I'd develop a better organization algorithm, because the one I used in this example is quite simple.
3. How would you implement finding the colors of the checkers and distinguishing which player the checker belongs to?
    I would segment each circle and extract the color features, maybe using the histogram. Then, classify the checkers that have similar features.
