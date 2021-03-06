#!/usr/bin/python3 
import cgi,cgitb
from os import ttyname
import time
cgitb.enable()
body = ""

def game():
    form_body = \
        """
<head>
    <meta charset="utf-8" />
    <title>Breakout Game</title>
    <style>
    	* { padding: 0; margin: 0; }
    	canvas { background: #eee; display: block; margin: 0 auto; }
    </style>
</head>
<body>

<canvas id="myCanvas" width="480" height="320"></canvas>

<script>
    class Ball
    {
        constructor(posX,posY,w)
        {
            this.canvas = document.getElementById("myCanvas");
            this.ctx = this.canvas.getContext("2d");
            this.posX = posX;
            this.posY = posY;
            this.width = w;
            this.dx = 2;
            this.dy = -2;
        }      

        draw() //วาดบอล
        {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.beginPath();
            this.ctx.arc(this.posX ,this.posY,this.width,0,Math.PI*2);
            this.ctx.fillStyle = "#0095DD";
            this.ctx.fill();
            this.ctx.closePath();
        }

        move()
        {
            this.posX = this.posX + this.dx;
            this.posY = this.posY + this.dy;    
        }
    }

    class Paddle
    {
        constructor(paddleX, paddleHeight, paddleWidth)
        {
            this.canvas = document.getElementById("myCanvas");
            this.ctx = this.canvas.getContext("2d");
            this.posX = paddleX;
            this.height = paddleHeight;
            this.width = paddleWidth;
        }
        
        draw() //วาดไม้
        {
            this.ctx.beginPath();
            this.ctx.rect(this.posX, this.canvas.height-this.height, this.width, this.height);
            this.ctx.fillStyle = "#0095DD";
            this.ctx.fill();
            this.ctx.closePath();
        }

        moveLeft()
        {
            this.posX -= 7;
            if (this.posX < 0) // when paddle over the border left of canvas
            {
                this.posX = 0; // set paddle at left
            }
        }

        moveRight()
        {
            this.posX += 7;
            if (this.posX + this.width > this.canvas.width) // when paddle over the border right of canvas
            {
                this.posX = this.canvas.width - this.width; // set paddle at right
            }
        }

        hitPaddle(posX)
        {
            // when the ball hit the paddle
            if (posX > this.posX && posX < this.posX + this.width) 
            {
               return true
            }
        }
    }


    class Brick
    {
        constructor(brickRow, brickColumn)
        {
            this.canvas = document.getElementById("myCanvas");
            this.ctx = this.canvas.getContext("2d");
            this.row = brickRow
            this.column = brickColumn
            this.width = 75
            this.height = 20
            this.padding = 10;
            this.offsetTop = 30;
            this.offsetLeft = 30;
            this.posX;
            this.posY;

            // สร้าง bricks ตามเเนว column เเละ row
            this.bricks = []
            for(var c=0;c<this.column;c++)
            {
                this.bricks[c] = [];
                for(var r=0; r<this.row; r++) 
                {
                    this.bricks[c][r] = {x:0, y:0, status:1};
                }
            }
        }

        draw()
        {
            for(var c=0; c<this.column; c++)
            {
                for(var r=0; r<this.row; r++)
                {
                    if (this.bricks[c][r].status == 1)  // if bricks remain
                    {
                        this.posX = (c*(this.width+this.padding))+this.offsetLeft;
                        this.posY = (r*(this.height+this.padding))+this.offsetTop;
                        this.bricks[c][r].x = this.posX;
                        this.bricks[c][r].y = this.posY;
                        this.ctx.beginPath();
                        this.ctx.rect(this.posX, this.posY, this.width, this.height);
                        this.ctx.fillStyle = "#0095DD";
                        this.ctx.fill();
                        this.ctx.closePath();
                    }
                }
            }
        }

        hitBrick(posX, posY)
        {
            
            for (var c= 0; c < this.column; c++)
            {
                for (var r = 0; r < this.row; r++) 
                {
                    // if bricks remain
                    if (this.bricks[c][r].status == 1)
                    {
                        // when ball hit that brick
                        if (posX > this.bricks[c][r].x && posX < this.bricks[c][r].x + this.width 
                        && posY > this.bricks[c][r].y && posY < this.bricks[c][r].y + this.height) 
                        {
                            this.bricks[c][r].status = 0;
                            return true;
                        }
                    }
                }
            }
            return false;
        }
    }
    
    class InputProcessor
    {
        addEvent()
        {
            document.addEventListener("keydown", this.keyDownHandler);
            document.addEventListener("mousemove", this.mouseMoveHandler, false);
        }
        
        keyDownHandler(e) 
        {
            // เมื่อกดปุ่มขวา
            if(e.key == "Right" || e.key == "ArrowRight") 
            {
                game.paddle.moveRight();
            }
            //เมื่อกดปุ่มซ้าย
            else if(e.key == "Left" || e.key == "ArrowLeft") 
            {
                game.paddle.moveLeft();
            }
        }

        mouseMoveHandler(e) 
        {
            var canvas = document.getElementById("myCanvas");
            // เมื่อ mouseX อยู่ใน canvas
            var relativeX = e.clientX - canvas.offsetLeft; 

            if (relativeX > 0 && relativeX < canvas.width) // when mouseX in canvas
            {
                game.paddle.posX = relativeX - game.paddle.width/2; // set paddle at mouse position
            }
        }
    }

    class BreakoutGame 
    {
        constructor() 
        {
            this.canvas = document.getElementById("myCanvas");
            this.ctx = this.canvas.getContext("2d");
            this.ball = new Ball(this.canvas.width/2, this.canvas.height-30, 10)
            this.paddle = new Paddle((this.canvas.width-75)/2, 10, 75)
            this.brick = new Brick(3,5)
            this.inputProcessor = new InputProcessor()
            this.inputProcessor.addEvent();
            this.lives = 3;
            this.score = 0;
        }

        draw() 
        {
            this.ball.draw();
            this.paddle.draw();
            this.brick.draw();
            this.ball.move();
            this.collisionDetection();
            this.updateGame();
            requestAnimationFrame(()=>this.draw());
        }

        updateGame() // แสดงคะเเนนกับชีวิตผู้เล่น
        {
            this.ctx.font = "16px Arial";
            this.ctx.fillStyle = "#0095DD";
            this.ctx.fillText("Score: " + this.score, 8, 20);
            this.ctx.fillText("Lives: "+ this.lives, this.canvas.width-65, 20);
        }

        collisionDetection()
        {
            //ตรวจสอบการชนของลูกบอล
            if (this.ball.posY+this.ball.dy > this.canvas.height-this.ball.width)
            {
                // the ball bounce when hit the paddle 
                if(this.paddle.hitPaddle(this.ball.posX))
                {
                    this.ball.dy = -this.ball.dy;
                }
                else
                {
                    this.lives -= 1;

                    // game over
                    if(!this.lives)
                    {
                        window.location.reload();
                        alert("Game Over")
                    }
                    else
                    {
                        // set position of the ball and the paddle at the start position
                        this.ball.posX = this.canvas.width/2;
                        this.ball.posY = this.canvas.height-30;
                        this.ball.dy = -3;
                        this.ball.dx = 3;
                        this.paddle.posX = (this.canvas.width-this.paddle.width)/2;
                    }
                }
            }

            // when the ball hit the brick
            if (this.brick.hitBrick(this.ball.posX, this.ball.posY))
            {
                this.ball.dy = -this.ball.dy;
                this.score += 1;
                this.winCheck();
            }

            // when the ball hit the left or right border of canvas
            if (this.ball.posX + this.ball.dx > this.canvas.width-this.ball.width || this.ball.posX + this.ball.dx < this.ball.width)
            {
                this.ball.dx = -this.ball.dx;
            }

            // when the ball hit the top border of canvas
            if (this.ball.posY + this.ball.dy < this.ball.width) 
            {
                this.ball.dy = -this.ball.dy;
            }
        }

        winCheck()
        {
            if (this.score == this.brick.row*this.brick.column)
            {
                //ถ้ากำแพงถูกทำลายทั้งหมด  
                alert("You are the Winner") //แสดงกล่องข้อความเเจ้งเตือนว่าชนะ
                window.location.reload(); // เรื่มเกมใหม่
            }
        }
    }


let game = new BreakoutGame();
game.draw();

</script>

</body>

        """
        
    return form_body


if __name__ == "__main__":
  print("Content-Type: text/html")
  print("<html>")
  print()
  body += game()
  print(body)
